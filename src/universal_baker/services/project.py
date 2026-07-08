from __future__ import annotations

import bpy


class ProjectService:
    @staticmethod
    def get(context):
        return context.scene.ubk_project

    @staticmethod
    def add_target_object(context, obj: bpy.types.Object):
        project = ProjectService.get(context)

        for item in project.objects:
            if item.target == obj:
                return item

        item = project.objects.add()
        item.target = obj
        project.active_object_index = len(project.objects) - 1
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
