from __future__ import annotations

from ..core.controller import BakeController
from .base import UBK_OT_Base


class UBK_OT_TargetObjectRemove(UBK_OT_Base):
    """Remove the selected bake target object."""

    bl_idname = "ubk.remove_target_object"
    bl_label = "Remove Bake Object"
    bl_description = "Remove the active object from the Universal Baker project"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        """Only enable the button when an object exists."""
        target_object = BakeController.active_target_object(context)
        return target_object is not None

    def execute(self, context):
        bake_group = BakeController.active_bake_group(context)
        if bake_group is None:
            return

        active_index = bake_group.active_target_object_index

        if active_index < 0:
            self.warning("No Target Object Selected.")

            return {"CANCELLED"}

        BakeController.remove_target_object(context, active_index)

        self.info("Target Object Removed.")

        return {"FINISHED"}


classes = (UBK_OT_TargetObjectRemove,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
