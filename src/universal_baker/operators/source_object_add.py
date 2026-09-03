from __future__ import annotations

from ..core.controller import BakeController
from .base import UBK_OT_Base


class UBK_OT_SourceObjectAdd(UBK_OT_Base):
    """Add selected mesh objects as Source Objects."""

    bl_idname = "ubk.add_source_object"
    bl_label = "Add Selected Source Objects"
    bl_description = "Add selected Target Objects to the Universal Baker project"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        """Only available when mesh objects are selected."""

        return any(obj.type == "MESH" for obj in context.selected_objects)

    def execute(self, context):
        objects = BakeController.add_selected_source_objects(context)

        if not objects:
            self.report({"WARNING"}, "No mesh objects were added.")

            return {"CANCELLED"}

        self.report({"INFO"}, f"Added {len(objects)} Source Object(s).")

        return {"FINISHED"}


classes = (UBK_OT_SourceObjectAdd,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
