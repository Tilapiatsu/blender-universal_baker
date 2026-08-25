from __future__ import annotations

from ..core.registry_definition import registry_definition
from .parameter_service_02 import ParameterService


class ProjectSynchronizer:
    @staticmethod
    def synchronize_project(
        project,
    ) -> None:

        for bake_group in project.bake_groups:
            for baker in bake_group.bakers:
                if not baker.is_custom:
                    continue

                definition = registry_definition.get(baker.baker)

                if definition is None:
                    continue

                ParameterService.synchronize(definition, baker.custom_baker)
