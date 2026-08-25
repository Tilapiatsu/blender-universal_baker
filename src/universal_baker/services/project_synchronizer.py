from __future__ import annotations

import bpy

from ..core.registry_definition import registry_definition
from .parameter_service import ParameterService
from ..properties.project import UBK_Project


class ProjectSynchronizer:
    @staticmethod
    def synchronize_project(project: UBK_Project) -> None:

        for bake_group in project.bake_groups:
            for baker in bake_group.bakers:
                if not baker.is_custom:
                    continue

                definition = registry_definition.get(baker.baker)

                if definition is None:
                    continue

                ParameterService.synchronize(definition, baker.custom_baker)

    @classmethod
    def synchronize_current_project(cls):
        cls.synchronize_project(bpy.context.scene.ubk_project)

    @classmethod
    def synchronize_blend_file(cls):
        for scene in bpy.data.scenes:
            cls.synchronize_project(scene.ubk_project)
