from __future__ import annotations

import bpy

from ..core.controller import BakeController
from ..runtime.job import Job
from .base import UBK_OT_Base


class UBK_OT_BakeAndPackAll(UBK_OT_Base):
    """Bake every enabled map of every enabled target object."""

    bl_idname = "ubk.bake_and_pack_all"
    bl_label = "Bake and Pack All"
    bl_description = "Bake every enabled map of every enabled target object and pack every packers at once"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        #
        # Let the controller decide if baking
        # is currently possible.
        #
        return True

    def execute(self, context):
        success, result = BakeController.bake_and_pack_all(context)

        if not success and isinstance(result, list):
            for error in result:
                self.error(error)

            return {"CANCELLED"}

        assert isinstance(result, Job)

        job: Job = result

        self.info(f"Created bake job with {job.total_tasks} task(s).")

        print(job)

        #
        # MVP
        #
        # Executor will be added later.
        #

        return {"FINISHED"}


classes = (UBK_OT_BakeAndPackAll,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
