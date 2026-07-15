from __future__ import annotations

import bpy

from ..core.controller import BakeController
from .base import UBK_OT_Base


class UBK_OT_PackAdd(UBK_OT_Base):
    """Add Pack item."""

    bl_idname = "ubk.add_pack"
    bl_label = "Add Pack"
    bl_description = "Add Pack item to Universal Baker project"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        pack = BakeController.add_pack(context)

        if not pack:
            self.report({"WARNING"}, "No pack item were added.")

            return {"CANCELLED"}

        self.report({"INFO"}, f"Added {pack.name} bake target(s).")

        return {"FINISHED"}


classes = (UBK_OT_PackAdd,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
