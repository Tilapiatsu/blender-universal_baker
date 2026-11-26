from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any
from uuid import uuid4

import bpy
from bpy_extras.io_utils import unique_name

from ..constant import NAME_DICT_BAKE_GROUP, NAME_DICT_BAKER, NAME_DICT_PACKER, get_prefs
from ..enum.execution import Execution
from ..executors.executor import Executor
from ..properties.object import UBK_SourceObject
from ..properties.packer import UBK_Packer
from ..runtime.job import Job
from ..runtime.runtime_manager import RuntimeManager
from ..runtime.task_accumulate import AccumulateTask
from ..runtime.task_bake import BakeTask
from ..runtime.task_mask_buffer import MaskBufferTask
from ..runtime.task_ownership_mask import UvOwnershipTask
from ..runtime.task_pack import PackingTask
from ..services.collection_bake_group import BakeGroupService
from ..services.collection_baker import BakerService
from ..services.collection_packer import PackerService
from ..services.collection_source_object import SourceObjectService
from ..services.collection_target_object import TargetObjectService
from ..services.internal_data import InternalDataService
from ..services.project import ProjectService
from .planner import ExecutionPlanner
from .registry_baker import registry_baker

if TYPE_CHECKING:
    from ..properties.bake_group import UBK_BakeGroup
    from ..properties.baker import UBK_Baker
    from ..properties.object import UBK_TargetObject


class BakeController:
    """Main application controller.

    The controller is the only public entry point for the
    baking system.

    UI operators should ONLY call this class.
    """

    @staticmethod
    def project(context: bpy.types.Context):
        return ProjectService.get(context)

    @classmethod
    def active_bake_group(cls, context: bpy.types.Context):
        return BakeGroupService.active(cls.project(context))

    @classmethod
    def active_target_object(cls, context: bpy.types.Context):
        bake_group = cls.active_bake_group(context)
        if bake_group is None:
            return

        return TargetObjectService.active(bake_group)

    @classmethod
    def active_source_object(cls, context: bpy.types.Context):
        target_object = cls.active_target_object(context)
        if target_object is None:
            return

        return SourceObjectService.active(target_object)

    @classmethod
    def active_baker(cls, context: bpy.types.Context):
        bake_group = cls.active_bake_group(context)
        if bake_group is None:
            return

        return BakerService.active(bake_group)

    @classmethod
    def active_packer(cls, context: bpy.types.Context):
        bake_group = cls.active_bake_group(context)
        if bake_group is None:
            return

        return PackerService.active(bake_group)

    # ---------------------------------------------------------
    # Bake Group Operations
    # ---------------------------------------------------------

    @classmethod
    def add_bake_group(cls, context: bpy.types.Context):
        item = ProjectService.add_bake_group(context)
        item.name = cls.get_unique_name("Group", item.uuid, NAME_DICT_BAKE_GROUP)
        return item

    @classmethod
    def remove_bake_group(cls, context: bpy.types.Context, index: int):
        project = cls.project(context)

        if project is None:
            return

        bake_group = project.bake_groups[index]

        if bake_group is None:
            return None

        NAME_DICT_BAKE_GROUP.pop(bake_group.uuid, None)
        return ProjectService.remove_bake_group(context, index)

    # ---------------------------------------------------------
    # Object Operations
    # ---------------------------------------------------------

    @classmethod
    def add_selected_target_objects(cls, context: bpy.types.Context):
        return ProjectService.add_selected_target_objects(context)

    @classmethod
    def remove_target_object(cls, context: bpy.types.Context, index: int):
        ProjectService.remove_target_object(context, index)

    @classmethod
    def add_selected_source_objects(cls, context: bpy.types.Context):
        return ProjectService.add_selected_source_objects(context)

    @classmethod
    def remove_source_object(cls, context: bpy.types.Context, index: int):
        ProjectService.remove_source_object(context, index)

    # ---------------------------------------------------------
    # Skew Correction
    # ---------------------------------------------------------

    @classmethod
    def remove_skew_image(cls, context: bpy.types.Context):
        target_object = cls.active_target_object(context)

        if not target_object:
            return None

        if target_object.settings_cage.skew_image is None:
            return None

        skew_map_name = target_object.settings_cage.skew_image.name
        if skew_map_name in bpy.data.images:
            bpy.data.images.remove(target_object.settings_cage.skew_image)

        target_object.settings_cage.skew_image = None

        return skew_map_name

    # ---------------------------------------------------------
    # Baker Operations
    # ---------------------------------------------------------
    @staticmethod
    def _unique_name_clean_func(name: str) -> str:
        word_pattern = re.compile(r"(\.[0-9]{3})$", re.IGNORECASE)
        name_iter = word_pattern.finditer(name)
        name_iter_match = [w.group(1) for w in name_iter]

        if len(name_iter_match) and name_iter_match[0] is not None:
            return name.replace(name_iter_match[0], "")
        else:
            return name

    @classmethod
    def get_unique_name(cls, name: str, obj: Any, name_dict: dict[Any, str]) -> str:
        name = unique_name(obj, name, name_dict, sep="_", clean_func=cls._unique_name_clean_func)

        return name

    @classmethod
    def add_baker(cls, context: bpy.types.Context, baker_id: str = "DIFFUSE"):
        bake_group = cls.active_bake_group(context)

        if not bake_group:
            return None

        producer = registry_baker[baker_id]
        if producer is None:
            return None

        baker = bake_group.bakers.add()
        baker.baker = baker_id
        baker.uuid = str(uuid4())
        baker.image_name = cls.get_unique_name(producer.name.title(), baker.uuid, NAME_DICT_BAKER)
        baker.previewable = producer.previewable
        bake_group.active_baker_index = len(bake_group.bakers) - 1

        # ProjectSynchronizer.synchronize_project(context.scene)

        return baker

    @classmethod
    def remove_baker(cls, context: bpy.types.Context):
        bake_group = cls.active_bake_group(context)

        if not bake_group:
            return

        if not bake_group.bakers:
            return

        NAME_DICT_BAKER.pop(bake_group.bakers[bake_group.active_baker_index].uuid, None)
        BakerService.remove(bake_group, bake_group.active_baker_index)

        if len(bake_group.bakers) == 0:
            runtime = RuntimeManager.current(context).bake_visualization
            if runtime.active:
                runtime.disable()
                project = cls.project(context)
                if project is None:
                    return
                project.visualization.refreshing = True
                project.visualization.enabled_preview = False
                project.visualization.enabled_display = False
                project.visualization.refreshing = False

    @staticmethod
    def resolve_map_uuid(project, uuid: str):
        for obj in project.objects:
            for map in obj.bakers:
                if map.uuid == uuid:
                    return map

        return None

    @classmethod
    def get_source_object_from_uuid(cls, uuid: str) -> UBK_SourceObject | None:
        project = cls.project(bpy.context)
        if project is None:
            return None

        for g in project.bake_groups:
            if not len(g.target_objects):
                continue

            for t in g.target_objects:
                for s in t.source_objects:
                    if s.uuid != uuid:
                        continue

                    return s

    @classmethod
    def get_target_object_from_uuid(cls, uuid: str) -> UBK_TargetObject | None:
        project = cls.project(bpy.context)
        if project is None:
            return None

        for g in project.bake_groups:
            if not len(g.target_objects):
                continue

            for t in g.target_objects:
                if t.uuid != uuid:
                    continue

                return t

    @classmethod
    def get_baker_from_uuid(cls, uuid: str) -> UBK_Baker | None:
        project = cls.project(bpy.context)
        if project is None:
            return None

        for g in project.bake_groups:
            if not len(g.bakers):
                continue

            for b in g.bakers:
                if b.uuid != uuid:
                    continue

                return b

    @classmethod
    def get_bake_group_from_uuid(cls, uuid: str) -> UBK_BakeGroup | None:
        project = cls.project(bpy.context)
        if project is None:
            return None

        for g in project.bake_groups:
            if g.uuid != uuid:
                continue

            return g

    @classmethod
    def get_paker_from_uuid(cls, uuid: str) -> UBK_Packer | None:
        project = cls.project(bpy.context)
        if project is None:
            return None

        for g in project.bake_groups:
            if not len(g.packers):
                continue

            for p in g.packers:
                if p.uuid != uuid:
                    continue

                return p

    # ---------------------------------------------------------
    # Pack Operations
    # ---------------------------------------------------------

    @classmethod
    def add_packer(cls, context: bpy.types.Context, packer_id: str = "INTERNAL"):
        bake_group = cls.active_bake_group(context)

        if not bake_group:
            return None

        packer = bake_group.packers.add()
        packer.uuid = str(uuid4())
        packer.image_name = cls.get_unique_name("Channel Packing", packer.uuid, NAME_DICT_PACKER)
        packer.packer = packer_id
        red = packer.mappings.add()
        green = packer.mappings.add()
        blue = packer.mappings.add()
        alpha = packer.mappings.add()

        red.source_channel = "R"
        green.source_channel = "G"
        blue.source_channel = "B"
        alpha.source_channel = "A"

        red.destination_channel = "R"
        green.destination_channel = "G"
        blue.destination_channel = "B"
        alpha.destination_channel = "A"

        bake_group.active_packer_index = len(bake_group.packers) - 1

        return packer

    @classmethod
    def remove_packer(cls, context: bpy.types.Context):
        bake_group = cls.active_bake_group(context)

        if bake_group is None:
            return

        if not bake_group.packers:
            return

        NAME_DICT_PACKER.pop(bake_group.packers[bake_group.active_packer_index].uuid, None)

        PackerService.remove(bake_group, bake_group.active_packer_index)

    # ---------------------------------------------------------
    # Internal Data
    # ---------------------------------------------------------

    @classmethod
    def ensure_output_node(cls, name: str):
        InternalDataService.ensure_output_node(name)

    @classmethod
    def get_output_node(cls, name: str):
        return InternalDataService.get_output_node(name)

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    @classmethod
    def validate(
        cls,
        context: bpy.types.Context,
        force_bake_group: bool = False,
        force_baker: bool = False,
    ) -> list[str]:
        errors = []

        project = cls.project(context)

        if not project.bake_groups:
            errors.append("No bake groups have been added.")

            return errors

        enabled_bake_groups = [g for g in project.bake_groups if g.enabled or force_bake_group]

        if not enabled_bake_groups:
            errors.append("Every Bake Groups is disabled.")

        for b in enabled_bake_groups:
            for o in b.target_objects:
                if o.object is None:
                    errors.append("A target object is missing.")

                    continue

            enabled_maps = [baker for baker in b.bakers if baker.enabled or force_baker]

            if not enabled_maps:
                errors.append(f"{b.name} has no enabled bake maps.")

        return errors

    # ---------------------------------------------------------
    # Planning
    # ---------------------------------------------------------

    @classmethod
    def create_job(
        cls,
        context: bpy.types.Context,
        register_bakers: bool = False,
        register_packers: bool = False,
        group_index: int = -1,
        baker_index: int = -1,
        target_index: int = -1,
        packer_index: int = -1,
    ) -> Job:
        planner = ExecutionPlanner()

        return planner.build_job(
            cls.project(context),
            register_bakers=register_bakers,
            register_packers=register_packers,
            group_index=group_index,
            baker_index=baker_index,
            target_index=target_index,
            packer_index=packer_index,
        )

    # ---------------------------------------------------------
    # Baking
    # ---------------------------------------------------------

    @classmethod
    def bake_all(cls, context: bpy.types.Context) -> tuple[bool, Job | list[str]]:
        errors = cls.validate(context)

        if errors:
            return (
                False,
                errors,
            )

        job = cls.create_job(context, register_bakers=True)

        project = cls.project(context)

        if project is None:
            return (False, ["Project is None"])

        use_maskers = project.use_maskers

        task_types = [BakeTask, AccumulateTask]

        if use_maskers:
            task_types += [UvOwnershipTask, MaskBufferTask]

        preferences = get_prefs()

        if preferences.use_background_blender:
            execution = Execution.EXTERNAL
        else:
            execution = Execution.INTERNAL

        executor = Executor(
            execution=execution,
            task_types=task_types,
        )
        executor.start_job(context, job)

        return (
            True,
            job,
        )

    @classmethod
    def bake_group(cls, context: bpy.types.Context, group_index: int) -> tuple[bool, Job | list[str]]:
        errors = cls.validate(context, force_bake_group=True, force_baker=True)

        if errors:
            return (
                False,
                errors,
            )

        job = cls.create_job(context, register_bakers=True, register_packers=True, group_index=group_index)

        project = cls.project(context)

        if project is None:
            return (False, ["Project is None"])

        use_maskers = project.use_maskers

        task_types = [BakeTask, AccumulateTask, PackingTask]

        if use_maskers:
            task_types += [UvOwnershipTask, MaskBufferTask]

        preferences = get_prefs()

        if preferences.use_background_blender:
            execution = Execution.EXTERNAL
        else:
            execution = Execution.INTERNAL

        executor = Executor(
            execution=execution,
            task_types=task_types,
        )
        executor.start_job(context, job)

        return (
            True,
            job,
        )

    @classmethod
    def bake_baker(cls, context: bpy.types.Context, baker_index: int) -> tuple[bool, Job | list[str]]:
        errors = cls.validate(context)

        if errors:
            return (
                False,
                errors,
            )

        job = cls.create_job(context, register_bakers=True, baker_index=baker_index)

        project = cls.project(context)

        if project is None:
            return (False, ["Project is None"])

        use_maskers = project.use_maskers

        task_types = [BakeTask, AccumulateTask]

        if use_maskers:
            task_types += [UvOwnershipTask, MaskBufferTask]

        preferences = get_prefs()

        if preferences.use_background_blender:
            execution = Execution.EXTERNAL
        else:
            execution = Execution.INTERNAL

        executor = Executor(
            execution=execution,
            task_types=task_types,
        )
        executor.start_job(context, job)

        return (
            True,
            job,
        )

    @classmethod
    def bake_target(cls, context: bpy.types.Context, target_index: int) -> tuple[bool, Job | list[str]]:
        errors = cls.validate(context)

        if errors:
            return (
                False,
                errors,
            )

        job = cls.create_job(context, register_bakers=True, target_index=target_index)

        project = cls.project(context)

        if project is None:
            return (False, ["Project is None"])

        use_maskers = project.use_maskers

        task_types = [BakeTask, AccumulateTask]

        if use_maskers:
            task_types += [UvOwnershipTask, MaskBufferTask]

        preferences = get_prefs()

        if preferences.use_background_blender:
            execution = Execution.EXTERNAL
        else:
            execution = Execution.INTERNAL

        executor = Executor(
            execution=execution,
            task_types=task_types,
        )
        executor.start_job(context, job)

        return (
            True,
            job,
        )

    # ---------------------------------------------------------
    # Paking
    # ---------------------------------------------------------

    @classmethod
    def pack_all(cls, context: bpy.types.Context) -> tuple[bool, Job | list[str]]:
        errors = []

        if errors:
            return (
                False,
                errors,
            )

        job = cls.create_job(context, register_packers=True)

        preferences = get_prefs()

        if preferences.use_background_blender:
            execution = Execution.EXTERNAL
        else:
            execution = Execution.INTERNAL

        executor = Executor(
            execution=execution,
            task_types=[
                PackingTask,
            ],
        )
        executor.start_job(context, job)

        return (
            True,
            job,
        )

    @classmethod
    def bake_and_pack_all(cls, context: bpy.types.Context) -> tuple[bool, Job | list[str]]:
        errors = cls.validate(context)

        if errors:
            return (
                False,
                errors,
            )

        job = cls.create_job(context, register_bakers=True, register_packers=True)

        project = cls.project(context)

        if project is None:
            return (False, ["Project is None"])

        use_maskers = project.use_maskers

        task_types = [BakeTask, AccumulateTask, PackingTask]

        if use_maskers:
            task_types += [UvOwnershipTask, MaskBufferTask]

        preferences = get_prefs()

        if preferences.use_background_blender:
            execution = Execution.EXTERNAL
        else:
            execution = Execution.INTERNAL

        executor = Executor(
            execution=execution,
            task_types=task_types,
        )
        executor.start_job(context, job)
        return (
            True,
            job,
        )

    @classmethod
    def pack_selected(cls, context: bpy.types.Context, packer_index: int) -> tuple[bool, Job | list[str]]:
        errors = []

        if errors:
            return (
                False,
                errors,
            )

        job = cls.create_job(context, register_packers=True, packer_index=packer_index)

        preferences = get_prefs()

        if preferences.use_background_blender:
            execution = Execution.EXTERNAL
        else:
            execution = Execution.INTERNAL

        executor = Executor(
            execution=execution,
            task_types=[
                PackingTask,
            ],
        )
        executor.start_job(context, job)

        return (
            True,
            job,
        )
