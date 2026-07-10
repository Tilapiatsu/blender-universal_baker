from __future__ import annotations

import bpy


class UBK_Preferences(bpy.types.AddonPreferences):
    """Addon preferences."""

    bl_idname = __package__

    assets_path: bpy.props.StringProperty(
        name="Assets Library",
        subtype="DIR_PATH",
        default="",
        description="Directory containing Universal Baker assets",
    )

    temp_directory: bpy.props.StringProperty(
        name="Temporary Directory",
        subtype="DIR_PATH",
        default="//",
    )

    use_background_blender: bpy.props.BoolProperty(
        name="Use Background Blender",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        col = layout.column()

        col.label(text="General")

        col.prop(self, "assets_path")
        col.prop(self, "temp_directory")

        layout.separator()

        layout.label(text="Experimental")

        layout.prop(self, "use_background_blender")


classes = (UBK_Preferences,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
