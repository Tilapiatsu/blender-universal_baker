from __future__ import annotations

from typing import List

import bpy

from .planner import BakePlanner
from ..runtime.job import Job

from ..services.project import ProjectService
from ..services.object import ObjectService
from ..services.map import MapService
from ..services.internal_data import InternalDataService
from ..constant import get_prefs
from ..runtime.executor_internal import BakeExecutorInternal
from ..runtime.executor_external import BakeExecutorExternal


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
    def active_map(cls, context):
        return MapService.active(cls.project(context))

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
        bake_map = object_settings.maps.add()
        bake_map.baker = baker_id
        bake_map.image_name = baker_id.title()
        object_settings.active_map_index = len(object_settings.maps) - 1

        return bake_map

    @classmethod
    def remove_map(cls, context):
        project = cls.project(context)

        obj = ObjectService.active(project)

        if not project.objects:
            return

        if obj is None:
            return

        object_settings = project.objects[project.active_object_index]

        if not object_settings.maps:
            return

        MapService.remove(project, obj.active_map_index)

    @staticmethod
    def resolve_map_uuid(project, uuid):
        for obj in project.objects:
            for map in obj.maps:
                if map.uuid == uuid:
                    return map

        return None

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
    def create_job(cls, context) -> Job:
        planner = BakePlanner()

        return planner.build_job(cls.project(context))

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

        job = cls.create_job(context)

        preferences = get_prefs()

        if preferences.use_background_blender:
            executor = BakeExecutorExternal()
        else:
            executor = BakeExecutorInternal()

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
