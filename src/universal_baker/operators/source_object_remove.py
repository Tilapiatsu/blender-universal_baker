from __future__ import annotations

from ..core.controller import BakeController
from .base import UBK_OT_Base


class UBK_OT_SourceObjectRemove(UBK_OT_Base):
    """Remove the selected bake target object."""

    bl_idname = "ubk.remove_source_object"
    bl_label = "Remove Source Object"
    bl_description = "Remove the active source object from the Universal Baker project"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        """Only enable the button when an source object exists."""
        source_object = BakeController.active_source_object(context)
        return source_object is not None

    def execute(self, context):
        target_object = BakeController.active_target_object(context)
        if target_object is None:
            return

        active_index = target_object.active_source_object_index

        if active_index < 0:
            self.warning("No bake object selected.")

            return {"CANCELLED"}

        BakeController.remove_source_object(context, active_index)

        self.info("Source Object Removed.")

        return {"FINISHED"}


classes = (UBK_OT_SourceObjectRemove,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
