from __future__ import annotations


from uuid import uuid4

from ..runtime.job import Job
from ..runtime.task_bake import BakeTask
from ..runtime.task_pack import PackingTask, PackingChannel
from ..packers.channels import Channel
from ..packers.packer_internal import PackerInternal
from ..core.registry_baker import registry_baker
from ..factories.settings_bake import BakeSettingsResolver
from ..factories.settings_cage import CageSettingsResolver
from ..factories.settings_pack import PackSettingsResolver


class ExecutionPlanner:
    """Converts the project into executable bake tasks."""

    def build_job(self, project) -> Job:
        job = Job()
        for obj in project.objects:
            if not obj.enabled:
                continue

            if obj.target is None:
                continue

            for bake_map in obj.bakers:
                if not bake_map.enabled:
                    continue

                settings = BakeSettingsResolver.resolve(
                    project.settings_bake,
                    bake_map.settings_bake if bake_map.override_settings else None,
                )
                # settings_cage = CageSettingsResolver.resolve(
                #     project.settings_cage,
                #     bake_map.settings_cage if bake_map.override_settings_cage else None,
                # )
                #
                task = BakeTask(
                    id=str(uuid4()),
                    enabled=True,
                    target=obj.target,
                    sources=obj.sources,
                    baker=registry_baker[bake_map.baker],
                    settings=settings,
                    image_name=bake_map.image_name,
                    # cage_object=None,
                    # settings_cage=settings_cage,
                )

                job.add_task(task)

            for pack in obj.packers:
                if not pack.enabled:
                    continue

                red = PackingChannel(
                    source_map_uuid=pack.mappings[0].source_map_uuid,
                    source_map_name=pack.mappings[0].source_map_items,
                    source_channel=Channel(pack.mappings[0].source_channel),
                    destination_channel=Channel(pack.mappings[0].destination_channel),
                )
                green = PackingChannel(
                    source_map_uuid=pack.mappings[1].source_map_uuid,
                    source_map_name=pack.mappings[1].source_map_items,
                    source_channel=Channel(pack.mappings[1].source_channel),
                    destination_channel=Channel(pack.mappings[1].destination_channel),
                )
                blue = PackingChannel(
                    source_map_uuid=pack.mappings[2].source_map_uuid,
                    source_map_name=pack.mappings[2].source_map_items,
                    source_channel=Channel(pack.mappings[2].source_channel),
                    destination_channel=Channel(pack.mappings[2].destination_channel),
                )
                alpha = PackingChannel(
                    source_map_uuid=pack.mappings[3].source_map_uuid,
                    source_map_name=pack.mappings[3].source_map_items,
                    source_channel=Channel(pack.mappings[3].source_channel),
                    destination_channel=Channel(pack.mappings[3].destination_channel),
                )

                pack_settings = PackSettingsResolver.resolve(
                    project.settings_pack,
                    pack.settings if pack.override_settings else None,
                )

                task = PackingTask(
                    id=str(uuid4()),
                    enabled=True,
                    packer=PackerInternal(),
                    image_name=pack.image_name,
                    settings=pack_settings,
                    red=red,
                    green=green,
                    blue=blue,
                    alpha=alpha,
                )
                job.add_task(task)

        return job
