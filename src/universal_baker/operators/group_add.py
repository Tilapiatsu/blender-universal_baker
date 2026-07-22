from __future__ import annotations

import bpy

from ..core.controller import BakeController
from .base import UBK_OT_Base


class UBK_OT_BakeGroupAdd(UBK_OT_Base):
    """Add a Bake Group into current project."""

    bl_idname = "ubk.add_bake_group"
    bl_label = "Add Bake Group"
    bl_description = "Add Bake Group to the Universal Baker project"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        group = BakeController.add_bake_group(context)

        if not group:
            self.report({"WARNING"}, "No bake group were added.")

            return {"CANCELLED"}

        self.report({"INFO"}, "Bake Group Added.")

        return {"FINISHED"}


classes = (UBK_OT_BakeGroupAdd,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
