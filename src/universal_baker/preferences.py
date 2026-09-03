from __future__ import annotations

from pathlib import Path
from bpy.props import StringProperty, BoolProperty, CollectionProperty, IntProperty
from bpy.types import PropertyGroup, AddonPreferences


class UBK_BakerLibraryFile(PropertyGroup):
    name: StringProperty(name="Name", default="Baker Name")
    path: StringProperty(
        name="Assets Path",
        subtype="DIR_PATH",
        default="",
    )
    builtin: BoolProperty(name="Builtin", default=False)


class UBK_BakerPath(PropertyGroup):
    name: StringProperty(name="Name", default="Baker Library")
    enabled: BoolProperty(name="Enabled", default=True)
    path: StringProperty(
        name="Assets Path",
        subtype="DIR_PATH",
        default="",
    )
    builtin: BoolProperty(name="Builtin", default=False)
    # files: CollectionProperty(type=UBK_BakerLibraryFile, name="Files")


class UBK_Preferences(AddonPreferences):
    """Addon preferences."""

    bl_idname = __package__

    active_baker_library_idx: IntProperty()
    baker_libraries: CollectionProperty(
        type=UBK_BakerPath,
        name="Baker Libraries",
        description="Directory containing Universal Bakers",
    )

    temp_directory: StringProperty(
        name="Temporary Directory",
        subtype="DIR_PATH",
        default="//",
    )

    use_background_blender: BoolProperty(
        name="Use Background Blender",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        col_general = layout.column()

        col_general.label(text="General")

        box = col_general.box()
        box.label(text="Baker Libraries")
        row = box.row(align=True)
        row.template_list(
            "UBK_UL_BakerLibraryList", "", self, "baker_libraries", self, "active_baker_library_idx", rows=5
        )

        col_box = row.column(align=True)
        col_box.operator("ubk.add_baker_library", text="", icon="ADD")
        col_box.operator("ubk.remove_baker_library", text="", icon="REMOVE")
        col_box.separator()
        col_box.operator("ubk.refresh_baker_library", text="", icon="FILE_REFRESH")

        if len(self.baker_libraries) and 0 <= self.active_baker_library_idx < len(self.baker_libraries):
            active_lib = self.baker_libraries[self.active_baker_library_idx]
            if active_lib is not None:
                col = box.column()
                col.prop(active_lib, "name")
                col.prop(active_lib, "path")
                if active_lib.builtin:
                    col.enabled = False

        col_general.prop(self, "temp_directory")

        layout.separator()

        layout.label(text="Experimental")

        layout.prop(self, "use_background_blender")


classes = (
    # UBK_BakerLibraryFile,
    UBK_BakerPath,
    UBK_Preferences,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    from .constant import get_prefs

    prefs = get_prefs()

    if len(prefs.baker_libraries) == 0:
        builtin = prefs.baker_libraries.add()
        builtin.name = "Builtin"
        builtin.builtin = True
        builtin.path = str(Path(__file__).parent.resolve() / "bakers_custom")


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
