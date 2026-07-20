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

    def build_job(self, project, regiter_bakers: bool = False, regiter_packers: bool = False) -> Job:
        from .controller import BakeController

        job = Job()
        for obj in project.objects:
            if not obj.enabled:
                continue

            if obj.target is None:
                continue

            for baker in obj.bakers:
                if regiter_bakers:
                    if not baker.enabled:
                        continue

                    settings = BakeSettingsResolver.resolve(
                        project.settings_bake,
                        baker.settings if baker.override_settings else None,
                    )
                    # settings_cage = CageSettingsResolver.resolve(
                    #     project.settings_cage,
                    #     bake_map.settings_cage if bake_map.override_settings_cage else None,
                    # )
                    #
                    task = BakeTask(
                        id=baker.name,
                        uuid=baker.uuid,
                        enabled=True,
                        target=obj.target,
                        sources=obj.sources,
                        baker=registry_baker[baker.baker],
                        settings=settings,
                        image_name=baker.image_name,
                        # cage_object=None,
                        # settings_cage=settings_cage,
                    )

                    job.add_task(task)

            if not regiter_packers:
                continue

            for pack in obj.packers:
                if not pack.enabled:
                    continue

                red_baker = BakeController.get_baker_from_uuid(pack.mappings[0].source_map_uuid)
                green_baker = BakeController.get_baker_from_uuid(pack.mappings[1].source_map_uuid)
                blue_baker = BakeController.get_baker_from_uuid(pack.mappings[2].source_map_uuid)
                alpha_baker = BakeController.get_baker_from_uuid(pack.mappings[3].source_map_uuid)

                red = PackingChannel(
                    source_map_uuid=pack.mappings[0].source_map_uuid,
                    source_map_name=red_baker.name if red_baker else "",
                    source_channel=Channel(pack.mappings[0].source_channel),
                    destination_channel=Channel(pack.mappings[0].destination_channel),
                )
                green = PackingChannel(
                    source_map_uuid=pack.mappings[1].source_map_uuid,
                    source_map_name=green_baker.name if green_baker else "",
                    source_channel=Channel(pack.mappings[1].source_channel),
                    destination_channel=Channel(pack.mappings[1].destination_channel),
                )
                blue = PackingChannel(
                    source_map_uuid=pack.mappings[2].source_map_uuid,
                    source_map_name=blue_baker.name if blue_baker else "",
                    source_channel=Channel(pack.mappings[2].source_channel),
                    destination_channel=Channel(pack.mappings[2].destination_channel),
                )
                alpha = PackingChannel(
                    source_map_uuid=pack.mappings[3].source_map_uuid,
                    source_map_name=alpha_baker.name if alpha_baker else "",
                    source_channel=Channel(pack.mappings[3].source_channel),
                    destination_channel=Channel(pack.mappings[3].destination_channel),
                )

                pack_settings = PackSettingsResolver.resolve(
                    project.settings_bake,
                    pack.settings if pack.override_settings else None,
                )

                task = PackingTask(
                    id=pack.name,
                    uuid=str(uuid4()),
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
