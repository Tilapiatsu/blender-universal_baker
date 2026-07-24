from __future__ import annotations

import bpy

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
from ..factories.settings_output import OutputSettingsResolver
from ..output.output_tokens import get_variables
from ..runtime.output_context import OutputContext


class ExecutionPlanner:
    """Converts the project into executable bake tasks."""

    def build_job(self, project, register_bakers: bool = False, register_packers: bool = False) -> Job:
        from .controller import BakeController

        job = Job()
        for group in project.bake_groups:
            if not group.enabled:
                continue

            for baker in group.bakers:
                if not register_bakers:
                    continue

                if not baker.enabled:
                    continue

                for obj in group.target_objects:
                    if obj.target is None:
                        continue

                    settings = BakeSettingsResolver.resolve(
                        project.settings_bake,
                        baker.settings if baker.override_settings else None,
                    )
                    # settings_cage = CageSettingsResolver.resolve(
                    #     project.settings_cage,
                    #     baker.settings_cage if baker.override_settings_cage else None,
                    # )

                    output_settings = OutputSettingsResolver.resolve(
                        project.settings_bake,
                        baker.settings if baker.override_settings else None,
                    )

                    output_context = OutputContext(
                        directory_template=output_settings.path.output_path,
                        filename_template=output_settings.path.filename_template,
                        extension=output_settings.image.file_format,
                        variables=get_variables(
                            bake_group_name=group.name,
                            baker=baker,
                            packer=None,
                            image_name=baker.image_name,
                            scene=bpy.context.scene,
                            extension=output_settings.image.file_format,
                        ),
                        output_settings=output_settings,
                    )

                    task = BakeTask(
                        bake_group=group,
                        id=baker.name,
                        uuid=baker.uuid,
                        enabled=True,
                        output_context=output_context,
                        target=obj.target,
                        sources=obj.sources,
                        baker=registry_baker[baker.baker],
                        settings=settings,
                        image_name=baker.image_name,
                        # cage_object=None,
                        # settings_cage=settings_cage,
                    )

                    job.add_task(task)

            if not register_packers:
                continue

            for packer in group.packers:
                if not packer.enabled:
                    continue

                red_baker = BakeController.get_baker_from_uuid(packer.mappings[0].source_map_uuid)
                green_baker = BakeController.get_baker_from_uuid(packer.mappings[1].source_map_uuid)
                blue_baker = BakeController.get_baker_from_uuid(packer.mappings[2].source_map_uuid)
                alpha_baker = BakeController.get_baker_from_uuid(packer.mappings[3].source_map_uuid)

                red = PackingChannel(
                    enabled=packer.mappings[0].enabled,
                    source_map_uuid=packer.mappings[0].source_map_uuid,
                    source_map_name=red_baker.baker if red_baker else "NONE",
                    source_channel=Channel(packer.mappings[0].source_channel),
                    destination_channel=Channel(packer.mappings[0].destination_channel),
                )
                green = PackingChannel(
                    enabled=packer.mappings[1].enabled,
                    source_map_uuid=packer.mappings[1].source_map_uuid,
                    source_map_name=green_baker.baker if green_baker else "NONE",
                    source_channel=Channel(packer.mappings[1].source_channel),
                    destination_channel=Channel(packer.mappings[1].destination_channel),
                )
                blue = PackingChannel(
                    enabled=packer.mappings[2].enabled,
                    source_map_uuid=packer.mappings[2].source_map_uuid,
                    source_map_name=blue_baker.baker if blue_baker else "NONE",
                    source_channel=Channel(packer.mappings[2].source_channel),
                    destination_channel=Channel(packer.mappings[2].destination_channel),
                )
                alpha = PackingChannel(
                    enabled=packer.mappings[3].enabled,
                    source_map_uuid=packer.mappings[3].source_map_uuid,
                    source_map_name=alpha_baker.baker if alpha_baker else "NONE",
                    source_channel=Channel(packer.mappings[3].source_channel),
                    destination_channel=Channel(packer.mappings[3].destination_channel),
                )

                pack_settings = PackSettingsResolver.resolve(
                    project.settings_bake,
                    packer.settings if packer.override_settings else None,
                )

                output_settings = OutputSettingsResolver.resolve(
                    project.settings_bake,
                    packer.settings if packer.override_settings else None,
                )
                output_context = OutputContext(
                    directory_template=output_settings.path.output_path,
                    filename_template=output_settings.path.filename_template,
                    extension=output_settings.image.file_format,
                    variables=get_variables(
                        bake_group_name=group.name,
                        baker=None,
                        packer=packer,
                        image_name=packer.image_name,
                        scene=bpy.context.scene,
                        extension=output_settings.image.file_format,
                    ),
                    output_settings=output_settings,
                )

                task = PackingTask(
                    id=packer.name,
                    uuid=str(uuid4()),
                    enabled=True,
                    output_context=output_context,
                    packer=PackerInternal(),
                    image_name=packer.image_name,
                    settings=pack_settings,
                    red=red,
                    green=green,
                    blue=blue,
                    alpha=alpha,
                )
                job.add_task(task)

        return job
