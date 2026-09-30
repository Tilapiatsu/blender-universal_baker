from __future__ import annotations

import bpy

from ..constant import LOG
from ..core.controller import BakeController
from .base import UBK_OT_Base


class UBK_OT_SkewCorrectionRemove(UBK_OT_Base):
    """Remove Skew Correction Image for the active target object"""

    bl_idname = "ubk.skew_correction_remove"
    bl_label = "Remove Skew Correction"
    bl_description = "Remove Skew Correction Image for the active target object"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        """Only available when a Target Object exists."""
        target_object = BakeController.active_target_object(context)
        return bool(target_object)

    def execute(self, context):
        skew_image_name = BakeController.remove_skew_image(context)

        if skew_image_name is None:
            self.warning("Unable to remove Skew image. No Skew image set")

            return {"CANCELLED"}

        self.info(f"Skew image '{skew_image_name}' removed.")

        return {"FINISHED"}


classes = (UBK_OT_SkewCorrectionRemove,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
