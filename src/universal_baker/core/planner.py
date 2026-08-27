from __future__ import annotations

import bpy

from uuid import uuid4

from universal_baker.runtime.label_set import LabelSet
from universal_baker.runtime.uv_ownership_mask import UvOwnershipMask


from ..constant import LOG
from ..runtime.task_ownership_mask import UvOwnershipTask
from ..runtime.settings_accumulate import AccumulateSettings
from ..runtime.job import Job
from ..runtime.task_bake import BakeTask
from ..runtime.task_pack import PackingTask, PackingChannel
from ..runtime.task_accumulate import AccumulateTask
from ..runtime.task_mask_buffer import MaskBufferTask
from ..runtime.tile_set import TileSet
from ..enum.channels import Channel
from ..core.registry_masker import registry_masker
from ..core.registry_baker import registry_baker
from ..core.registry_packer import registry_packer
from ..core.registry_accumulator import registry_accumulator
from ..factories.settings_bake import BakeSettingsResolver
from ..factories.settings_cage import CageSettingsResolver
from ..factories.settings_pack import PackSettingsResolver
from ..factories.settings_output import OutputContextResolver, UvOwnershipOutputContextResolver
from ..services.uv import UVService
from ..resources.uv import UVLayout
from ..resources.ownership import OwnershipDatas
from ..enum.image_layout import ImageLayout


class ExecutionPlanner:
    """Converts the project into executable bake tasks."""

    def build_job(
        self,
        project,
        register_bakers: bool = False,
        register_packers: bool = False,
        group_index: int = -1,
        baker_index: int = -1,
        packer_index: int = -1,
    ) -> Job:
        with LOG.scope("Planner"):
            from .controller import BakeController

            job = Job()
            for grp_idx, group in enumerate(project.bake_groups):
                if group_index == -1:
                    if not group.enabled:
                        continue
                elif group_index >= 0 and grp_idx == group_index:
                    pass
                else:
                    continue

                #
                # Store UDIM Uv Informations
                #
                object_tiles = {}
                group_tiles = tuple()
                object_uuids = {}
                ownership_datas = OwnershipDatas()
                for index, obj in enumerate(group.target_objects):
                    if not obj.enabled:
                        continue

                    if obj.object is None:
                        continue

                    ownership_datas.add(name=obj.object.name, uuid=obj.uuid, uv_layer=obj.uv_layer)

                    udim_tiles = tuple()

                    if group.detect_udim:
                        udim_tiles = UVService.detect_udim_tiles(obj.object, obj.uv_layer)
                        LOG.info(f"{len(udim_tiles)} udim tile(s) detected for {obj.object.name}:")
                        LOG.info(f"{udim_tiles}")
                        for u in udim_tiles:
                            LOG.info(str(UVService.tile_number(u[0], u[1])))

                        # using set to prevent duplication
                        group_tiles = tuple(set(group_tiles).union(set(udim_tiles)))

                        object_tiles[obj.object.name] = udim_tiles

                    object_uuids[index] = obj.uuid

                uv_layout = UVLayout(
                    image_layout=ImageLayout.UDIM if group.detect_udim else ImageLayout.SINGLE,
                    udim_tiles=group_tiles,
                )

                output_context = UvOwnershipOutputContextResolver.resolve(
                    group=group, scene=bpy.context.scene, global_settings=project.settings_bake
                )

                #
                # Create UvOwnershipTask
                #
                ownership_mask = UvOwnershipMask(
                    labels=LabelSet(),
                    resolution=(
                        output_context.output_settings.path.width,
                        output_context.output_settings.path.height,
                    ),
                    object_index_uuids=object_uuids,
                )

                ownership_task = UvOwnershipTask(
                    uuid=str(uuid4()),
                    name="UVOwnership",
                    enabled=True,
                    output_context=output_context,
                    bake_group_uuid=group.uuid,
                    uv_layout=uv_layout,
                    result=TileSet(),
                    ownership_datas=ownership_datas,
                    ownership_mask=ownership_mask,
                )

                job.add_task(ownership_task)

                for bk_idx, baker in enumerate(group.bakers):
                    if not register_bakers:
                        continue

                    if baker_index == -1:
                        if not baker.enabled:
                            continue
                    elif baker_index >= 0 and bk_idx == baker_index:
                        pass
                    else:
                        continue

                    settings = BakeSettingsResolver.resolve(
                        project.settings_bake,
                        baker.settings if baker.override_settings else None,
                    )
                    # settings_cage = CageSettingsResolver.resolve(
                    #     project.settings_cage,
                    #     baker.settings_cage if baker.override_settings_cage else None,
                    # )

                    output_context = OutputContextResolver.resolve(
                        group_name=group.name,
                        baker=baker,
                        scene=bpy.context.scene,
                        global_settings=project.settings_bake,
                        override_settings=baker.settings if baker.override_settings else None,
                    )
                    has_multiple_targets = len([o for o in group.target_objects if o.enabled]) > 1

                    for obj in group.target_objects:
                        if not obj.enabled:
                            continue

                        if obj.object is None:
                            continue

                        if obj.object.name not in object_tiles:
                            LOG.error(f"{obj.object.name} have invalid UV.")
                            # TODO: need to properly deal with the case of one object doesn't have UV -> Should skip the
                            # obj, not the entire tasks
                            # TODO: Need to deeper test non UDIM cases
                            continue

                        uv_layout = UVLayout(
                            image_layout=ImageLayout.UDIM if group.detect_udim else ImageLayout.SINGLE,
                            udim_tiles=object_tiles[obj.object.name],
                        )

                        task = BakeTask(
                            name=baker.image_name,
                            bake_group_uuid=group.uuid,
                            uuid=baker.uuid,
                            enabled=True,
                            output_context=output_context,
                            target_object_uuid=obj.uuid,
                            sources=obj.sources,
                            producer=registry_baker[baker.baker],
                            settings=settings,
                            image_name=baker.image_name,
                            has_multiple_targets=has_multiple_targets,
                            uv_layer=obj.uv_layer,
                            uv_layout=uv_layout,
                            result=TileSet(),
                            # cage_object=None,
                            # settings_cage=settings_cage,
                        )

                        job.add_task(task)

                        task = MaskBufferTask(
                            uv_ownership_task=ownership_task,
                            uuid=str(uuid4()),
                            baker_uuid=baker.uuid,
                            target_object_uuid=obj.uuid,
                            name=obj.object.name,
                            enabled=True,
                            output_context=output_context,
                            bake_group_uuid=group.uuid,
                            uv_layout=uv_layout,
                            has_multiple_targets=has_multiple_targets,
                            producer=registry_masker["APPLY_MASK"],
                            result=TileSet(),
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
                        name=baker.image_name,
                        uuid=str(uuid4()),
                        enabled=True,
                        output_context=output_context,
                        bake_group_uuid=group.uuid,
                        baker_name=baker.baker,
                        baker_uuid=baker.uuid,
                        producer=registry_accumulator[registry_baker[baker.baker].accumulator_id],
                        image_name=baker.image_name,
                        settings=settings_accumulator,
                        uv_layout=uv_layout,
                        result=TileSet(),
                    )
                    job.add_task(task)

                if not register_packers:
                    continue

                uv_layout = UVLayout(
                    image_layout=ImageLayout.UDIM if group.detect_udim else ImageLayout.SINGLE,
                    udim_tiles=group_tiles,
                )

                for pk_idx, packer in enumerate(group.packers):
                    if packer_index == -1:
                        if not packer.enabled:
                            continue
                    elif packer_index >= 0 and pk_idx == packer_index:
                        pass
                    else:
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

                    output_context = OutputContextResolver.resolve(
                        group_name=group.name,
                        scene=bpy.context.scene,
                        global_settings=project.settings_bake,
                        packer=packer,
                        override_settings=packer.settings if packer.override_settings else None,
                    )

                    task = PackingTask(
                        name=packer.name,
                        uuid=str(uuid4()),
                        bake_group_uuid=group.uuid,
                        enabled=True,
                        output_context=output_context,
                        producer=registry_packer[packer.packer],
                        image_name=packer.image_name,
                        settings=pack_settings,
                        red=red,
                        green=green,
                        blue=blue,
                        alpha=alpha,
                        uv_layout=uv_layout,
                        result=TileSet(),
                    )
                    job.add_task(task)

            with LOG.scope("Planner"):
                LOG.info(str(job))
            return job
