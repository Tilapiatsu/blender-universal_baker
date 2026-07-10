from __future__ import annotations

from ..runtime.job import BakeJob
from ..runtime.task import BakeTask
from ..core.registry import registry


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
                    target=obj.target,
                    sources=obj.sources,
                    baker=registry[bake_map.baker],
                    output=bake_map.output,
                )

                job.add_task(task)

        return job
