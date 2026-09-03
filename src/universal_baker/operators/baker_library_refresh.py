from __future__ import annotations


from .base import UBK_OT_Base
from ..bakers.custom import refresh


class UBK_OT_BakerlibraryRefresh(UBK_OT_Base):
    """Refresh baker library items."""

    bl_idname = "ubk.refresh_baker_library"
    bl_label = "Refresh Baker library"
    bl_description = "Refresh a new baker library to Universal Baker's preferences"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        refresh()

        return {"FINISHED"}


classes = (UBK_OT_BakerlibraryRefresh,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
