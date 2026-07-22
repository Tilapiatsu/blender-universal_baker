from __future__ import annotations

import bpy

from ..core.controller import BakeController
from ..runtime.job import Job
from .base import UBK_OT_Base


class UBK_OT_BakeGroup(UBK_OT_Base):
    """Bake every enabled map of selecvted target object."""

    bl_idname = "ubk.bake_group"
    bl_label = "Bake Group"
    bl_description = "Bake every enabled map of current Bake Group"
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
        success, result = BakeController.bake_group(context, self.index)

        if not success:
            for error in result:
                self.error(error)

            return {"CANCELLED"}

        job: Job = result

        self.info(f"Created bake job with {job.total_tasks} task(s).")

        print(job)

        #
        # MVP
        #
        # Executor will be added later.
        #

        return {"FINISHED"}


classes = (UBK_OT_BakeGroup,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
