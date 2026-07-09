from __future__ import annotations

import bpy

from ..core.controller import BakeController
from .base import UBK_OT_Base


class UBK_OT_ObjectAdd(UBK_OT_Base):
    """Add selected mesh objects as bake targets."""

    bl_idname = "ubk.add_object"
    bl_label = "Add Selected Objects"
    bl_description = "Add selected mesh objects to the Universal Baker project"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        """Only available when mesh objects are selected."""

        return any(obj.type == "MESH" for obj in context.selected_objects)

    def execute(self, context):
        objects = BakeController.add_selected_objects(context)

        if not objects:
            self.report({"WARNING"}, "No mesh objects were added.")

            return {"CANCELLED"}

        self.report({"INFO"}, f"Added {len(objects)} bake target(s).")

        return {"FINISHED"}


classes = (UBK_OT_ObjectAdd,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
