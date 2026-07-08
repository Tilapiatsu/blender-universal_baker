from __future__ import annotations

from .job import BakeJob
from .task import BakeTask


class BakePlanner:
    """Converts the project into executable bake tasks."""

    def build_job(self, project) -> BakeJob:
        job = BakeJob()
        for obj in project.objects:
            if not obj.enabled:
                continue

            if obj.target is None:
                continue

            for bake_map in obj.maps:
                if not bake_map.enabled:
                    continue

                task = BakeTask(
                    object_name=obj.target.name,
                    baker_id=bake_map.baker,
                    image_name=bake_map.image_name,
                )

                job.add_task(task)

        return job
