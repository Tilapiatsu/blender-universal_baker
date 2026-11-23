# Blender logger UI integration

The generic logger remains independent of Blender. This package provides the
Blender-specific filter properties, entry toggle operator, redraw adapter,
drawing helpers, and an optional runtime composition class.

## Registration

Register the logger UI integration before registering panels that draw it:

```python
from .logger import blender as logger_blender

logger_runtime = None


def register():
    logger_blender.register(property_name="myaddon_logger_filter")

    # Register your addon panel classes here.
    register_classes()

    global logger_runtime
    logger_runtime = logger_blender.BlenderLoggerRuntime(
        addon_name="My Addon",
        filter_property_name="myaddon_logger_filter",
        space_types={"VIEW_3D"},
    )


def unregister():
    global logger_runtime

    # Panels must be unregistered before the logger integration.
    unregister_classes()

    if logger_runtime is not None:
        logger_runtime.close()
        logger_runtime = None

    logger_blender.unregister()
```

Use a unique WindowManager property name when embedding the logger in multiple
addons. The default name is `logger_filter`.

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
        return logger_runtime is not None

    def draw(self, context):
        if logger_runtime is None:
            return

        logger_blender.draw_logger_panel(
            self.layout,
            context,
            logger_runtime,
        )
```

Alternatively, call `draw_log_tree(layout, runtime.ui_sink)` if you want to
build your own filter UI.

## Logging messages with details

```python
try:
    perform_operation()
except Exception as exc:
    runtime.logger.error(
        "Operation failed",
        exception=exc,
        display_in_ui=True,
        data={
            "object": object_name,
            "operation": "Bake",
        },
    )
```

The logger captures a formatted traceback when the event is created. The UI
can then show the full stored traceback without reconstructing it during draw.

Ordinary messages must explicitly opt into the UI with `display_in_ui=True`.
Scope lifecycle entries are visible by default unless their metadata sets
`display_in_ui=False`.
