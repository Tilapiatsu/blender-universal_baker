import bpy


class LoggerFilterProperties(bpy.types.PropertyGroup):
    show_debug: bpy.props.BoolProperty(
        name="Debug",
        description="Show DEBUG messages",
        default=False,
    )

    show_info: bpy.props.BoolProperty(
        name="Info",
        description="Show INFO messages",
        default=True,
    )

    show_warning: bpy.props.BoolProperty(
        name="Warning",
        description="Show WARNING messages",
        default=True,
    )

    show_error: bpy.props.BoolProperty(
        name="Error",
        description="Show ERROR and CRITICAL messages",
        default=True,
    )
