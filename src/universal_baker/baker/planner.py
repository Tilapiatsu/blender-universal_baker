import bpy
from .task import BakeTask
from .job import BakeJob
# from pathlib import Path


class BakePlanner:
    def build(self, project):
        job = BakeJob()
        tasks = []
        for obj in project.objects:
            if not obj.enabled:
                continue

            for bake_map in obj.maps:
                if not bake_map.enabled:
                    continue

                tasks.append(
                    BakeTask(
                        target=obj,
                        bake_map=bake_map,
                        # output_path=output_path
                    )
                )

        return tasks
