from __future__ import annotations

from ..runtime.job import BakeJob
from ..runtime.task import BakeTask
from ..core.registry import registry
from ..factories.bake_settings import BakeSettingsResolver
from ..factories.cage_settings import CageSettingsResolver


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

                bake_settings = BakeSettingsResolver.resolve(
                    project.bake_settings,
                    bake_map.bake_settings if bake_map.override_bake_settings else None,
                )
                cage_settings = CageSettingsResolver.resolve(
                    project.cage_settings,
                    bake_map.cage_settings if bake_map.override_cage_settings else None,
                )

                task = BakeTask(
                    target=obj.target,
                    sources=obj.sources,
                    baker=registry[bake_map.baker],
                    bake_settings=bake_settings,
                    image_name=bake_map.image_name,
                    cage_object=None,
                    cage_settings=cage_settings,
                )

                job.add_task(task)

        return job
