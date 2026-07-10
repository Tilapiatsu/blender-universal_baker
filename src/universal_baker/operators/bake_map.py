from __future__ import annotations

import bpy

from ..core.controller import BakeController
from ..runtime.job import BakeJob
from .base import UBK_OT_Base
from ..services.project import ProjectService
from ..services.object import ObjectService


class UBK_OT_BakeMap(UBK_OT_Base):
    """Bake selected map."""

    bl_idname = "ubk.bake_map"
    bl_label = "Bake Map"
    bl_description = "Bake current Map"
    bl_options = {"REGISTER"}

    index: bpy.props.IntProperty(name="Index", default=0)

    @classmethod
    def poll(cls, context):
        #
        # Let the controller decide if baking
        # is currently possible.
        #
        return True

    def execute(self, context):
        success, result = BakeController.bake_object(context, self.index)

        if not success:
            for error in result:
                self.error(error)

            return {"CANCELLED"}

        job: BakeJob = result

        self.info(f"Created bake job with {job.total_tasks} task(s).")

        print(job)

        #
        # MVP
        #
        # Executor will be added later.
        #

        return {"FINISHED"}


classes = (UBK_OT_BakeMap,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
