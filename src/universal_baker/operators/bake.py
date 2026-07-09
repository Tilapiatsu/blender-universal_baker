from __future__ import annotations

import bpy

from ..core.controller import BakeController
from ..runtime.job import BakeJob
from .base import UBK_OT_Base


class UBK_OT_BakeAll(UBK_OT_Base):
    """Bake every enabled map of every enabled target object."""

    bl_idname = "ubk.bake_all"
    bl_label = "Bake All"
    bl_description = "Bake every enabled map of every enabled target object"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        #
        # Let the controller decide if baking
        # is currently possible.
        #
        return True

    def execute(self, context):
        success, result = BakeController.bake_all(context)

        # --------------------------------------------------------------
        # Validation failed
        # --------------------------------------------------------------

        if not success:
            for error in result:
                self.error(error)

            return {"CANCELLED"}

        job: BakeJob = result

        self.info(f"Created bake job with {job.total_tasks} task(s).")

        self.print_job(job)

        #
        # MVP
        #
        # Executor will be added later.
        #

        return {"FINISHED"}

    # -------------------------------------------------------------------------
    # Debug
    # -------------------------------------------------------------------------

    @staticmethod
    def print_job(
        job: BakeJob,
    ):

        print()

        print("=" * 60)
        print("Universal Baker")
        print("Bake Job")
        print("=" * 60)

        for index, task in enumerate(job.tasks):
            print(f"{index + 1:03d} | {task.object_name:20} | {task.baker_id}")

        print("-" * 60)

        print(f"Total Tasks : {job.total_tasks}")

        print("=" * 60)
        print()
