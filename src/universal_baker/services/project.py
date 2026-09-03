from __future__ import annotations

from uuid import uuid4

import bpy

from ..constant import LOG
from .collection_bake_group import BakeGroupService
from .collection_target_object import TargetObjectService


class ProjectService:
    @staticmethod
    def get(context):
        return context.scene.ubk_project

    @staticmethod
    def add_bake_group(context: bpy.types.context):
        project = ProjectService.get(context)

        item = project.bake_groups.add()
        item.uuid = str(uuid4())

        project.active_bake_group_index = len(project.bake_groups) - 1

        return item

    @staticmethod
    def remove_bake_group(context: bpy.types.Context, index: int):
        project = ProjectService.get(context)

        if not project.bake_groups:
            return

        project.bake_groups.remove(index)

        project.active_bake_group_index = min(
            project.active_bake_group_index,
            len(project.bake_groups) - 1,
        )

    @staticmethod
    def add_target_object(context, obj: bpy.types.Object):
        project = ProjectService.get(context)

        if not project.bake_groups:
            return

        bake_group = BakeGroupService.active(project)

        if not bake_group:
            return

        for item in bake_group.target_objects:
            if item.object == obj:
                return item

        item = bake_group.target_objects.add()
        item.object = obj
        item.uuid = str(uuid4())

        bake_group.active_target_object_index = len(bake_group.target_objects) - 1
        return item

    @staticmethod
    def add_selected_target_objects(context):
        created = []

        for obj in context.selected_objects:
            if obj.type != "MESH":
                continue

            created.append(
                ProjectService.add_target_object(
                    context,
                    obj,
                )
            )

        return created

    @staticmethod
    def remove_target_object(context, index: int):
        project = ProjectService.get(context)

        if not project.bake_groups:
            return

        bake_group = BakeGroupService.active(project)

        if not bake_group:
            return

        bake_group.target_objects.remove(index)

        bake_group.active_target_object_index = min(
            bake_group.active_target_object_index,
            len(bake_group.target_objects) - 1,
        )

    @staticmethod
    def add_selected_source_objects(context):
        created = []

        project = ProjectService.get(context)

        if not project.bake_groups:
            return

        bake_group = BakeGroupService.active(project)

        if not bake_group:
            return

        targets = [t.object for t in bake_group.target_objects]

        for obj in context.selected_objects:
            if obj.type != "MESH":
                continue

            if obj in targets:
                LOG.warning(f"{obj.name} is already a target object. It can't be added as source")
                continue

            created.append(
                ProjectService.add_source_object(
                    context,
                    obj,
                )
            )

        return created

    @staticmethod
    def add_source_object(context, obj: bpy.types.Object):
        project = ProjectService.get(context)

        if not project.bake_groups:
            return

        bake_group = BakeGroupService.active(project)

        if not bake_group:
            return

        target_object = TargetObjectService.active(bake_group)

        if not target_object:
            return

        for item in target_object.source_objects:
            if item.object == obj:
                return item

        item = target_object.source_objects.add()
        item.object = obj

        target_object.active_source_object_index = len(target_object.source_objects) - 1
        return item

    @staticmethod
    def remove_source_object(context, index: int):
        project = ProjectService.get(context)

        if not project.bake_groups:
            return

        bake_group = BakeGroupService.active(project)

        if not bake_group:
            return

        target_object = TargetObjectService.active(bake_group)

        if not target_object:
            return

        target_object.source_objects.remove(index)

        target_object.active_source_object_index = min(
            target_object.active_source_object_index,
            len(target_object.source_objects) - 1,
        )

    @staticmethod
    def clear(context):
        project = ProjectService.get(context)
        project.objects.clear()
        project.active_object_index = 0

    @staticmethod
    def get_active_object_index(context) -> int:
        project = ProjectService.get(context)
        return project.active_object_index
