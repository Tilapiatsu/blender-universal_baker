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


def register():
    register_logger_ui(property_name="ubk_logger_filter")
    for m in modules:
        m.register()


def unregister():
    # Close active modal jobs while Blender classes, the logger and its sinks
    # are still available. Their generator finally blocks restore scene state.
    from .constant import LOG, LOG_RUNTIME
    from .logger.blender.modal import cancel_all_modal_tasks

    cancel_all_modal_tasks()

    if LOG_RUNTIME is not None:
        LOG_RUNTIME.close()

    LOG.close()

    for m in reversed(modules):
        m.unregister()
    unregister_logger_ui()
