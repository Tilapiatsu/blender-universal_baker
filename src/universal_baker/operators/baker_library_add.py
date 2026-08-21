from __future__ import annotations

import bpy

from ..constant import LOG, get_prefs
from .base import UBK_OT_Base
from ..bakers.custom import refresh


class UBK_OT_BakerlibraryAdd(UBK_OT_Base):
    """Add a baker library item."""

    bl_idname = "ubk.add_baker_library"
    bl_label = "Add Baker library"
    bl_description = "Add a new baker library to Universal Baker's preferences"
    bl_options = {"REGISTER", "UNDO"}

    name: bpy.props.StringProperty(
        name="Library Name",
        description="Name of the library to add",
        default="Library",
    )
    path: bpy.props.StringProperty(
        name="Path",
        description="Directory path where the .blend files are located",
        default="//",
        subtype="DIR_PATH",
    )

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "name")
        layout.prop(self, "path")

    def execute(self, context):
        preferences = get_prefs()

        lib = preferences.baker_libraries.add()
        lib.name = self.name
        lib.enabled = True
        lib.path = self.path
        preferences.active_baker_library_idx = len(preferences.baker_libraries) - 1

        if context.area:
            context.area.tag_redraw()

        refresh()

        return {"FINISHED"}


classes = (UBK_OT_BakerlibraryAdd,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
