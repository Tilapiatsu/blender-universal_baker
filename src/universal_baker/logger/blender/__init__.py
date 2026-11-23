import bpy

from .operators import (
    LOGGER_OT_ToggleEntry,
    clear_registered_sinks,
)
from .properties import LoggerFilterProperties

_registered_property_name = None


def register(property_name: str = "logger_filter"):
    """
    Register the Blender logger UI classes and WindowManager filter settings.

    Use a namespaced property name when embedding this logger in multiple
    addons, e.g. "ubk_logger_filter".
    """
    global _registered_property_name

    if _registered_property_name is not None:
        if _registered_property_name != property_name:
            raise RuntimeError(
                f"Blender logger integration is already registered with property '{_registered_property_name}'"
            )
        return

    bpy.utils.register_class(LoggerFilterProperties)

    try:
        setattr(
            bpy.types.WindowManager,
            property_name,
            bpy.props.PointerProperty(type=LoggerFilterProperties),
        )
        bpy.utils.register_class(LOGGER_OT_ToggleEntry)
    except Exception:
        if hasattr(bpy.types.WindowManager, property_name):
            delattr(bpy.types.WindowManager, property_name)

        bpy.utils.unregister_class(LoggerFilterProperties)
        raise

    _registered_property_name = property_name


def unregister():
    global _registered_property_name

    if _registered_property_name is None:
        return

    # Runtimes should be closed before unregistering this module.
    clear_registered_sinks()

    if hasattr(bpy.types.WindowManager, _registered_property_name):
        delattr(bpy.types.WindowManager, _registered_property_name)

    bpy.utils.unregister_class(LOGGER_OT_ToggleEntry)
    bpy.utils.unregister_class(LoggerFilterProperties)

    _registered_property_name = None


from .draw import draw_log_tree, draw_logger_panel
from .runtime import BlenderLoggerRuntime

__all__ = [
    "BlenderLoggerRuntime",
    "draw_log_tree",
    "draw_logger_panel",
    "register",
    "unregister",
]
