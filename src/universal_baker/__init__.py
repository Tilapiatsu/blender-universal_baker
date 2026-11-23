bl_info = {
    "name": "Universal Baker",
    "author": "Tilapiatsu",
    "version": (1, 0, 0),
    "blender": (4, 5, 0),
    "description": "Blender Baking Made Easy",
    "category": "Render",
}

# from . import registration
#
# modules = (registration,)

from . import (
    accumulators,
    assets,
    bakers,
    bakers_custom,
    compositors,
    executors,
    handlers,
    maskers,
    operators,
    output,
    packers,
    parameters_definition,
    preferences,
    properties,
    ui,
)
from .logger.blender import BlenderLoggerRuntime
from .logger.blender import (
    register as register_logger_ui,
)
from .logger.blender import (
    unregister as unregister_logger_ui,
)

modules = (
    preferences,
    output,
    ui,
    operators,
    bakers,
    bakers_custom,
    parameters_definition,
    properties,
    executors,
    compositors,
    packers,
    accumulators,
    maskers,
    handlers,
    assets,
)


logger_runtime = None


def register():
    global logger_runtime
    register_logger_ui(property_name="ubk_logger_filter")
    logger_runtime = BlenderLoggerRuntime(
        addon_name="Universal Baker",
        filter_property_name="ubk_logger_filter",
        space_types={"VIEW_3D"},
    )
    for m in modules:
        m.register()


def unregister():
    global logger_runtime
    for m in reversed(modules):
        m.unregister()

    if logger_runtime is not None:
        logger_runtime.close()
        logger_runtime = None

    unregister_logger_ui()
