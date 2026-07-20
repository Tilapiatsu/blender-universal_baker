from __future__ import annotations

from typing import List

import bpy
from uuid import uuid4

from ..resources.image import ImageResource

from .planner import ExecutionPlanner
from ..runtime.job import Job

from ..services.project import ProjectService
from ..services.object import ObjectService
from ..services.packer import PackService
from ..services.map import BakerService
from ..services.internal_data import InternalDataService
from ..constant import get_prefs
from ..core.registry_executor import registry_executor

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..properties.baker import UBK_Baker


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
    def active_object(cls, context):
        return ObjectService.active(cls.project(context))

    @classmethod
    def active_baker(cls, context):
        return BakerService.active(cls.project(context))

    @classmethod
    def active_packer(cls, context):
        return PackService.active(cls.active_object(context))

    # ---------------------------------------------------------
    # Object Operations
    # ---------------------------------------------------------

    @classmethod
    def add_selected_objects(cls, context):
        return ProjectService.add_selected_objects(context)

    @classmethod
    def remove_object(cls, context, index: int):
        ProjectService.remove_object(context, index)

    # ---------------------------------------------------------
    # Map Operations
    # ---------------------------------------------------------

    @classmethod
    def add_map(cls, context, baker_id: str = "DIFFUSE"):
        project = cls.project(context)

        if not project.objects:
            return None

        object_settings = project.objects[project.active_object_index]
        baker = object_settings.bakers.add()
        baker.baker = baker_id
        baker.image_name = baker_id.title()
        baker.uuid = str(uuid4())
        object_settings.active_baker_index = len(object_settings.bakers) - 1

        return baker

    @classmethod
    def remove_map(cls, context):
        project = cls.project(context)

        if not project.objects:
            return

        obj = ObjectService.active(project)

        if obj is None:
            return

        if not obj.bakers:
            return

        BakerService.remove(project, obj.active_baker_index)

    @staticmethod
    def resolve_map_uuid(project, uuid):
        for obj in project.objects:
            for map in obj.bakers:
                if map.uuid == uuid:
                    return map

        return None

    @classmethod
    def get_resource_from_uuid(cls, uuid: str) -> ImageResource | None:
        project = cls.project(bpy.context)
        if project is None:
            return None

        for o in project.objects:
            if not len(o.bakers):
                continue

            for b in o.bakers:
                if b.uuid == uuid:
                    resource = ImageResource(
                        image=b.image,
                        name=b.image_name,
                    )
                    if b.image is not None:
                        resource.width = b.image.size[0]
                        resource.height = b.image.size[1]
                    else:
                        return None

                    return resource

    @classmethod
    def get_baker_from_uuid(cls, uuid: str) -> UBK_Baker | None:
        project = cls.project(bpy.context)
        if project is None:
            return None

        for o in project.objects:
            if not len(o.bakers):
                continue

            for b in o.bakers:
                if b.uuid == uuid:
                    return b

    # ---------------------------------------------------------
    # Pack Operations
    # ---------------------------------------------------------

    @classmethod
    def add_packer(cls, context, packer_id: str = "INTERNAL"):
        project = cls.project(context)

        if not project.objects:
            return

        obj = ObjectService.active(project)

        if obj is None:
            return

        packer = obj.packers.add()
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

        obj.active_packer_index = len(obj.packers) - 1

        return packer

    @classmethod
    def remove_packer(cls, context, index: int = 0):
        project = cls.project(context)

        if not project.objects:
            return

        obj = ObjectService.active(project)

        if obj is None:
            return

        PackService.remove(obj, index)

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
    def validate(cls, context) -> List[str]:
        errors = []

        project = cls.project(context)

        if not project.objects:
            errors.append("No target objects have been added.")

            return errors

        enabled_objects = [obj for obj in project.objects if obj.enabled]

        if not enabled_objects:
            errors.append("Every target object is disabled.")

        for obj in enabled_objects:
            if obj.target is None:
                errors.append("A target object is missing.")

                continue

            # enabled_maps = [bake_map for bake_map in obj.maps if bake_map.enabled]
            #
            # if not enabled_maps:
            #     errors.append(f"{obj.target.name} has no enabled bake maps.")

        return errors

    # ---------------------------------------------------------
    # Planning
    # ---------------------------------------------------------

    @classmethod
    def create_job(cls, context, register_bakers: bool = False, register_packers: bool = False) -> Job:
        planner = ExecutionPlanner()

        return planner.build_job(cls.project(context), register_bakers, register_packers)

    # ---------------------------------------------------------
    # Baking
    # ---------------------------------------------------------

    @classmethod
    def bake_all(cls, context) -> tuple[bool, Job | list[str]]:
        errors = cls.validate(context)

        if errors:
            return (
                False,
                errors,
            )

        job = cls.create_job(context, register_bakers=True)

        preferences = get_prefs()

        if preferences.use_background_blender:
            executor = registry_executor["BakeExternal"]
        else:
            executor = registry_executor["BakeInternal"]

        executor.execute(context, job)

        #
        # MVP
        #
        # Executor will be added later.
        #

        return (
            True,
            job,
        )

    @classmethod
    def bake_object(cls, context, object_index: int):

        #
        # TODO
        #
        raise NotImplementedError()

    @classmethod
    def bake_map(cls, context, object_index: int, map_index: int):

        #
        # TODO
        #
        raise NotImplementedError()

    # ---------------------------------------------------------
    # Paking
    # ---------------------------------------------------------

    @classmethod
    def pack_all(cls, context) -> tuple[bool, Job | list[str]]:
        errors = cls.validate(context)

        if errors:
            return (
                False,
                errors,
            )

        job = cls.create_job(context, register_packers=True)

        preferences = get_prefs()

        if preferences.use_background_blender:
            executor = registry_executor["PackExternal"]
        else:
            executor = registry_executor["PackInternal"]

        executor.execute(context, job)

        #
        # MVP
        #
        # Executor will be added later.
        #

        return (
            True,
            job,
        )

    @classmethod
    def bake_and_pack_all(cls, context) -> tuple[bool, Job | list[str]]:
        success_bake, job_bake = cls.bake_all(context)
        if not success_bake:
            return success_bake, job_bake

        success_pack, job_pack = cls.pack_all(context)
        if not success_pack:
            return success_pack, job_pack

        return success_pack, job_pack

    @classmethod
    def pack_selected(cls, context, object_index: int):

        #
        # TODO
        #
        raise NotImplementedError()
