# Blender logger UI integration

The generic `Logger` is configured by the addon. `BlenderLoggerRuntime` does
not impose a sink or middleware preset: it receives an already configured
logger and optionally connects one `UISink` to Blender's UI.

## Configure the logger outside the runtime

```python
from .logger import Logger, Severity
from .logger.sinks.console import ConsoleSink
from .logger.sinks.file import FileSink
from .logger.sinks.ui.sink import UISink
from .logger.middleware.prefix import PrefixMiddleware
from .logger.middleware.statistics import StatisticsMiddleware

logger = Logger(addon="My Addon")

# Middleware is addon-specific and is registered directly on the logger.
logger.middleware.add(PrefixMiddleware("[My Addon]"), name="prefix")
logger.middleware.add(StatisticsMiddleware(), name="statistics")

# Declare only the sinks this addon needs.
ui_sink = UISink()
logger.dispatcher.add_sink("ui", ui_sink)
logger.dispatcher.add_sink(
    "file",
    FileSink(filename="my_addon.log", level=Severity.DEBUG),
)
logger.dispatcher.add_sink(
    "console",
    ConsoleSink(level=Severity.WARNING),
)
```

An addon that needs only a file sink can omit `UISink`, `BlenderLoggerRuntime`,
and the Blender logger UI registration entirely:

```python
logger = Logger(addon="Batch Tool")
logger.dispatcher.add_sink("file", FileSink())
logger.middleware.add(MyMiddleware())
```

## Initialize Blender UI integration

Register the Blender UI classes/properties only when this addon uses a
`UISink`. Do this before registering panels that draw the logger.

```python
from .logger import blender as logger_blender

logger_runtime = None

def register():
    global logger_runtime

    logger_blender.register(property_name="myaddon_logger_filter")

    # Configure logger, middleware, and sinks before creating the runtime.
    # `logger` and `ui_sink` are created by your addon configuration.
    logger_runtime = logger_blender.BlenderLoggerRuntime(
        logger=logger,
        ui_sink=ui_sink,
        filter_property_name="myaddon_logger_filter",
        space_types={"VIEW_3D"},
    )

    register_classes()


def unregister():
    global logger_runtime

    unregister_classes()

    if logger_runtime is not None:
        logger_runtime.close()
        logger_runtime = None

    # The runtime is closed before the UI operator/property classes disappear.
    logger_blender.unregister()

    # The addon owns the logger and closes its sinks.
    logger.close()
```

`ui_sink` must be the exact same instance that was registered with
`logger.dispatcher.add_sink(...)`. If no UI sink is passed, the runtime creates
no redraw adapter and registers no sink for the UI toggle operator.

`BlenderLoggerRuntime.close()` only releases Blender integration resources.
It intentionally does not call `logger.close()`.

## Panel

```python
import bpy

from .logger import blender as logger_blender


class MYADDON_PT_Logger(bpy.types.Panel):
    bl_idname = "MYADDON_PT_logger"
    bl_label = "Execution Log"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "My Addon"

    @classmethod
    def poll(cls, context):
        return (
            logger_runtime is not None
            and logger_runtime.ui_sink is not None
        )

    def draw(self, context):
        logger_blender.draw_logger_panel(
            self.layout,
            context,
            logger_runtime,
        )
```

If you prefer to build your own filter UI, call
`draw_log_tree(layout, ui_sink, ui_filter=...)` directly.

## Logging messages with details

```python
try:
    perform_operation()
except Exception as exc:
    logger.error(
        "Operation failed",
        exception=exc,
        display_in_ui=True,
        data={
            "object": object_name,
            "operation": "Bake",
        },
    )
```

Ordinary messages must explicitly opt into the UI with `display_in_ui=True`.
Scope lifecycle entries are visible by default unless their metadata sets
`display_in_ui=False`.

## Detached scopes

A detached scope is created without inheriting the currently active synchronous
scope. It has its own lifecycle/tree position and can be bound temporarily when
logging from callbacks:

```python
scope = logger.detached_scope("Texture export", ui_channel="EXPORT")

with scope:
    with logger.bind_scope(scope):
        logger.info("Preparing export", display_in_ui=True)
        scope.set_progress(0.25)
```

`with scope:` starts and completes the scope. `with logger.bind_scope(scope):`
only changes log attribution temporarily; it does not change lifecycle state.
For cooperative cancellation, call `scope.request_cancel()` and periodically
call `scope.raise_if_cancelled()` in the task. `scope.cancel()` remains the
immediate terminal-state operation for synchronous callers.

## Modal task execution

Register the Blender integration with `logger.blender.register()` before
starting modal tasks. A task is an iterator/generator that yields periodically;
Blender gets an event-loop turn between timer ticks:

```python
from logger.blender import ModalTaskRunner, TaskProgress


def export_task():
    total = len(items)
    for index, item in enumerate(items):
        export_one(item)  # Keep each individual step reasonably short.
        yield TaskProgress((index + 1) / total, f"Exported {item.name}")
    return "Export complete"


runner = ModalTaskRunner(
    logger,
    interval=0.05,
    steps_per_tick=1,
    on_complete=lambda result: print(result),
)
runner.start(bpy.context, export_task())
```

Press **Esc** or **Right Mouse** to cancel. A task can also observe
`scope.raise_if_cancelled()` if it receives/uses its scope. The runner creates a
detached root scope automatically; pass `scope=...` to supply a pre-created
pending scope. Keep individual yielded steps short: modal execution prevents
Blender's UI from being blocked between steps, but cannot interrupt a single
long-running Python or Blender API call.

`TaskProgress.progress` is normalized to 0..1. Yielding a number is shorthand
for a progress update. Yield `TaskProgress(message="...")` to update the task
log without changing progress. The generator's `return` value is passed to
`on_complete`.

The modal runner executes on Blender's main thread. Detached scopes provide
lifecycle/context independence, not permission to call Blender's Python API
from worker threads. For CPU-heavy work, split the algorithm into bounded
steps or move only pure-Python work to a worker and marshal Blender data access
back to the main thread.
