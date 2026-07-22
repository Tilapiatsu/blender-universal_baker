from __future__ import annotations

import bpy

from ..core.controller import BakeController
from .base import UBK_OT_Base


class UBK_OT_BakeGroupRemove(UBK_OT_Base):
    """Add a Bake Group into current project."""

    bl_idname = "ubk.remove_bake_group"
    bl_label = "Remove Bake Group"
    bl_description = "Remove Bake Group from the Universal Baker project"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        project = BakeController.project(context)
        return len(project.bake_groups)

    def execute(self, context):
        project = BakeController.project(context)

        active_index = project.active_bake_group_index

        if active_index < 0:
            self.warning("No bake group selected.")

            return {"CANCELLED"}

        BakeController.remove_bake_group(context, active_index)

        self.info("Bake group removed.")

        return {"FINISHED"}


classes = (UBK_OT_BakeGroupRemove,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
