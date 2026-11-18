from __future__ import annotations

from ..constant import LOG

from ..core.controller import BakeController
from ..runtime.job import Job
from .base import UBK_OT_Base


class UBK_OT_BakeAll(UBK_OT_Base):
    """Bake every enabled map of every enabled target object."""

    bl_idname = "ubk.bake_all"
    bl_label = "Bake All"
    bl_description = "Bake every enabled map of every enabled target object"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context) -> bool:
        project = BakeController.project(context)
        active_bake_group = BakeController.active_bake_group(context)

        if len(project.bake_groups) == 0:
            return False

        return len(active_bake_group.target_objects) > 0 and len(active_bake_group.bakers) > 0

    def execute(self, context):
        success, result = BakeController.bake_all(context)

        if not success and isinstance(result, list):
            for error in result:
                self.error(error)

            return {"CANCELLED"}

        assert isinstance(result, Job)

        job: Job = result

        self.info(f"Created bake job with {job.total_tasks} task(s).")

        return {"FINISHED"}


classes = (UBK_OT_BakeAll,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
