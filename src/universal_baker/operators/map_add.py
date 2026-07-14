from __future__ import annotations

import bpy

from ..core.controller import BakeController
from ..services.project import ProjectService
from ..services.object import ObjectService
from ..services.internal_data import InternalDataService
from .base import UBK_OT_Base


class UBK_OT_MapAdd(UBK_OT_Base):
    """Add a bake map to the active bake object."""

    bl_idname = "ubk.add_map"
    bl_label = "Add Bake Map"
    bl_description = "Add a new bake map to the active Universal Baker object"
    bl_options = {"REGISTER", "UNDO"}

    baker_id: bpy.props.StringProperty(name="Baker", description="Identifier of the baker to add", default="DIFFUSE")

    @classmethod
    def poll(cls, context):
        """Only available when a bake object exists."""

        project = ProjectService.get(context)
        return bool(project.objects)

    def execute(self, context):
        bake_map = BakeController.add_map(context, baker_id=self.baker_id)

        if bake_map is None:
            self.warning("Unable to add bake map. Select a target object first.")

            return {"CANCELLED"}

        project = ProjectService.get(context)
        InternalDataService.ensure_output_node(project.bake_settings.internal_name)

        obj = ObjectService.active(project)
        assert obj is not None
        bake_map.bake_settings.internal_name = f"{obj.target.name}_{self.baker_id}"
        InternalDataService.ensure_output_node(bake_map.bake_settings.internal_name)

        self.info(f"Added bake map '{self.baker_id}'.")

        return {"FINISHED"}


classes = (UBK_OT_MapAdd,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
