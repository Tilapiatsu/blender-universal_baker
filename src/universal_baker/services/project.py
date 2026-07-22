from __future__ import annotations

import bpy

from .bake_group import BakeGroupService


class ProjectService:
    @staticmethod
    def get(context):
        return context.scene.ubk_project

    @staticmethod
    def add_bake_group(context: bpy.types.context):
        project = ProjectService.get(context)

        item = project.bake_groups.add()

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
            if item.target == obj:
                return item

        item = bake_group.target_objects.add()
        item.target = obj
        project.active_object_index = len(bake_group.target_objects) - 1
        return item

    @staticmethod
    def add_selected_objects(context):
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
    def remove_object(context, index: int):
        project = ProjectService.get(context)

        if not project.objects:
            return

        project.objects.remove(index)

        project.active_object_index = min(
            project.active_object_index,
            len(project.objects) - 1,
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
