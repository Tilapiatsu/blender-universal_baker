from __future__ import annotations

import bpy

from ..baker.controller import BakeController
from ..services.project import ProjectService
from ..services.object import ObjectService
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

        project = ProjectService.get(context)
        return bool(project.objects)

    def execute(self, context):
        project = ProjectService.get(context)

        active_index = project.active_object_index

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
