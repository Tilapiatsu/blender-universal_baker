from __future__ import annotations

import bpy

from ..constant import LOG
from ..core.registry_definition import registry_definition
from ..properties.project import UBK_Project
from .parameter_service import ParameterService


class ProjectSynchronizer:
    @staticmethod
    def synchronize_project(project: UBK_Project) -> None:

        for bake_group in project.bake_groups:
            for baker in bake_group.bakers:
                LOG.debug(f"Synchronize parameter for baker : {baker.baker}")
                definition = registry_definition.get(baker.baker)

                if definition is None:
                    LOG.debug("Definition not Found")
                    continue

                ParameterService.synchronize(definition, baker.custom_baker)

    @classmethod
    def synchronize_current_project(cls):
        cls.synchronize_project(bpy.context.scene.ubk_project)

    @classmethod
    def synchronize_blend_file(cls):
        for scene in bpy.data.scenes:
            cls.synchronize_project(scene.ubk_project)
