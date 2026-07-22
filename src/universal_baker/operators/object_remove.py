from __future__ import annotations

from ..core.controller import BakeController
from .base import UBK_OT_Base


class UBK_OT_ObjectRemove(UBK_OT_Base):
    """Remove the selected bake target object."""

    bl_idname = "ubk.remove_object"
    bl_label = "Remove Bake Object"
    bl_description = "Remove the active object from the Universal Baker project"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        """Only enable the button when an object exists."""
        bake_group = BakeController.active_bake_group(context)
        if bake_group is None:
            return False
        return bool(bake_group.target_objects)

    def execute(self, context):
        bake_group = BakeController.active_bake_group(context)
        if bake_group is None:
            return

        active_index = bake_group.active_target_object_index

        if active_index < 0:
            self.warning("No bake object selected.")

            return {"CANCELLED"}

        BakeController.remove_object(context, active_index)

        self.info("Bake object removed.")

        return {"FINISHED"}


classes = (UBK_OT_ObjectRemove,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
