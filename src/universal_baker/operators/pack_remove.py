from __future__ import annotations

import bpy

from ..core.controller import BakeController
from .base import UBK_OT_Base


class UBK_OT_ObjectRemove(UBK_OT_Base):
    """Remove the selected bake target object."""

    bl_idname = "ubk.remove_packer"
    bl_label = "Remove packer item"
    bl_description = "Remove the active packer from the Universal Baker project"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        """Only enable the button when packer exists."""

        project = BakeController.project(context)
        return bool(project.packers)

    def execute(self, context):
        project = BakeController.project(context)

        active_index = project.active_packer_index

        if active_index < 0:
            self.warning("No packer item selected.")

            return {"CANCELLED"}

        BakeController.remove_packer(context, active_index)

        self.info("Packer item removed.")

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
