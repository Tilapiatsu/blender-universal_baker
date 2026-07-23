from __future__ import annotations

import bpy

from ..core.controller import BakeController
from .base import UBK_OT_Base


class UBK_OT_PackerRemove(UBK_OT_Base):
    """Remove the selected bake target object."""

    bl_idname = "ubk.remove_packer"
    bl_label = "Remove packer item"
    bl_description = "Remove the active packer from the Universal Baker project"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        """Only enable the button when packer exists."""
        bake_group = BakeController.active_bake_group(context)

        if bake_group is None:
            return False

        return bool(bake_group.packers)

    def execute(self, context):
        packer = BakeController.active_packer(context)
        if packer is None:
            self.error("No Packer found.")
            return {"CANCELLED"}

        BakeController.remove_packer(context)

        self.info("Packer item removed.")

        return {"FINISHED"}


classes = (UBK_OT_PackerRemove,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
