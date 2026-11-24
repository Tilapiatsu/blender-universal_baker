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
