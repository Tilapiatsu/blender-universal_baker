from __future__ import annotations

import bpy

from ..core.controller import BakeController
from .base import UBK_OT_Base


class UBK_OT_PackMappingFix(UBK_OT_Base):
    """Add Pack item."""

    bl_idname = "ubk.packer_mapping_fix"
    bl_label = "Fix Packer"
    bl_description = "Add Packer item to Universal Baker project"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        pack = BakeController.add_packer(context)

        if not pack:
            self.report({"WARNING"}, "No packer item were added.")

            return {"CANCELLED"}

        self.report({"INFO"}, f"Added {pack.name} packer Item.")

        return {"FINISHED"}


classes = (UBK_OT_PackMappingFix,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
