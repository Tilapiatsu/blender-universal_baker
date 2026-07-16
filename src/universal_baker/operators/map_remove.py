from __future__ import annotations

import bpy

from ..core.controller import BakeController
from .base import UBK_OT_Base


class UBK_OT_MapRemove(UBK_OT_Base):
    """Remove the active bake map."""

    bl_idname = "ubk.remove_map"
    bl_label = "Remove Bake Map"
    bl_description = "Remove the active bake map from the selected bake object"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        """Only available when the active bake object contains maps."""

        obj = BakeController.active_object(context)

        if obj is None:
            return False

        return bool(obj.maps)

    def execute(self, context):

        bake_map = BakeController.active_baker(context)

        if bake_map is None:
            self.warning("No bake map selected.")

            return {"CANCELLED"}

        BakeController.remove_map(context)

        self.info("Bake map removed.")

        return {"FINISHED"}


classes = (UBK_OT_MapRemove,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
