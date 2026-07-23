from __future__ import annotations

import bpy

from ..core.controller import BakeController
from .base import UBK_OT_Base


class UBK_OT_BakerAdd(UBK_OT_Base):
    """Add a bake map to the active bake object."""

    bl_idname = "ubk.add_baker"
    bl_label = "Add Baker"
    bl_description = "Add a new baker map to the active Universal Baker object"
    bl_options = {"REGISTER", "UNDO"}

    baker_id: bpy.props.StringProperty(name="Baker", description="Identifier of the baker to add", default="DIFFUSE")

    @classmethod
    def poll(cls, context):
        """Only available when a bake object exists."""
        bake_group = BakeController.active_bake_group(context)
        return bool(bake_group)

    def execute(self, context):
        baker = BakeController.add_baker(context, baker_id=self.baker_id)

        if baker is None:
            self.warning("Unable to add bake map. Select a target object first.")

            return {"CANCELLED"}

        project = BakeController.project(context)
        BakeController.ensure_output_node(project.settings_bake.internal_name)

        baker.settings.internal_name = f"{self.baker_id}"
        BakeController.ensure_output_node(baker.settings.internal_name)

        self.info(f"Added bake map '{self.baker_id}'.")

        return {"FINISHED"}


classes = (UBK_OT_BakerAdd,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
