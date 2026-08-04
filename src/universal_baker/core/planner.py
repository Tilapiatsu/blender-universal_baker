from __future__ import annotations

import bpy

from uuid import uuid4


from ..constant import LOG
from ..runtime.settings_accumulate import AccumulateSettings
from ..runtime.job import Job
from ..runtime.task_bake import BakeTask
from ..runtime.task_pack import PackingTask, PackingChannel
from ..runtime.task_accumulate import AccumulateTask
from ..enum.channels import Channel
from ..core.registry_baker import registry_baker
from ..core.registry_packer import registry_packer
from ..core.registry_accumulator import registry_accumulator
from ..factories.settings_bake import BakeSettingsResolver
from ..factories.settings_cage import CageSettingsResolver
from ..factories.settings_pack import PackSettingsResolver
from ..factories.settings_output import OutputSettingsResolver
from ..output.output_tokens import get_variables
from ..runtime.output_context import OutputContext
from ..services.uv import UVService
from ..resources.uv import UVLayout
from ..enum.image_layout import ImageLayout


class ExecutionPlanner:
    """Converts the project into executable bake tasks."""

    def build_job(self, project, register_bakers: bool = False, register_packers: bool = False) -> Job:
        with LOG.scope("Planner"):
            from .controller import BakeController

            job = Job()
            for group in project.bake_groups:
                if not group.enabled:
                    continue

                image_layout = ImageLayout.UDIM if group.detect_udim else ImageLayout.SINGLE

                group_tiles = tuple()

                for baker in group.bakers:
                    if not register_bakers:
                        continue

                    if not baker.enabled:
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

                    has_multiple_targets = len([o for o in group.target_objects if o.enabled]) > 1

                    for obj in group.target_objects:
                        if obj.object is None:
                            continue

                        udim_tiles = tuple()

                        if group.detect_udim:
                            udim_tiles = UVService.detect_udim_tiles(obj.object, obj.uv_layer)
                            LOG.info(f"{len(udim_tiles)} udim tile(s) detected for {obj.object.name}:")
                            LOG.info(f"{udim_tiles}")
                            for u in udim_tiles:
                                LOG.info(str(UVService.tile_number(u[0], u[1])))

                            # using set to prevent duplication
                            group_tiles = tuple(set(group_tiles).union(set(udim_tiles)))

                        uv_layout = UVLayout(
                            image_layout=ImageLayout.UDIM if group.detect_udim else ImageLayout.SINGLE,
                            udim_tiles=udim_tiles,
                        )

                        task = BakeTask(
                            bake_group_uuid=group.uuid,
                            id=baker.name,
                            uuid=baker.uuid,
                            enabled=True,
                            output_context=output_context,
                            target_object_uuid=obj.uuid,
                            sources=obj.sources,
                            baker=registry_baker[baker.baker],
                            settings=settings,
                            image_name=baker.image_name,
                            has_multiple_targets=has_multiple_targets,
                            uv_layer=obj.uv_layer,
                            uv_layout=uv_layout,
                            # cage_object=None,
                            # settings_cage=settings_cage,
                        )

                        job.add_task(task)

                    if not has_multiple_targets:
                        continue

                    uv_layout = UVLayout(
                        image_layout=ImageLayout.UDIM if group.detect_udim else ImageLayout.SINGLE,
                        udim_tiles=group_tiles,
                    )

                    settings_accumulator = AccumulateSettings(baker_uuid=baker.uuid)
                    task = AccumulateTask(
                        uuid=baker.uuid,
                        enabled=True,
                        output_context=output_context,
                        bake_group_uuid=group.uuid,
                        baker_name=baker.baker,
                        baker_uuid=baker.uuid,
                        accumulator=registry_accumulator[registry_baker[baker.baker].accumulator_id],
                        image_name=baker.image_name,
                        settings=settings_accumulator,
                        uv_layout=uv_layout,
                    )
                    job.add_task(task)

                if not register_packers:
                    continue

                uv_layout = UVLayout(
                    image_layout=ImageLayout.UDIM if group.detect_udim else ImageLayout.SINGLE,
                    udim_tiles=group_tiles,
                )

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
                        bake_group_uuid=group.uuid,
                        enabled=True,
                        output_context=output_context,
                        packer=registry_packer[packer.packer],
                        image_name=packer.image_name,
                        settings=pack_settings,
                        red=red,
                        green=green,
                        blue=blue,
                        alpha=alpha,
                        uv_layout=uv_layout,
                    )
                    job.add_task(task)

            with LOG.scope("Planner"):
                LOG.info(str(job))
            return job
