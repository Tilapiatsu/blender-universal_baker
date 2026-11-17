from __future__ import annotations

import bpy

from ..constant import LOG
from ..core.registry_baker import registry_baker
from ..core.registry_definition import registry_definition
from ..enum.image_colorspace import ImageColorSpace
from ..enum.view_transform import DisplayDevice, ViewTransform
from ..parameter.baker_custom.definition import CustomBakerDefinition
from ..runtime.color_management_info import ColorManagementInfo
from ..runtime.runtime_manager import RuntimeManager
from .parameter_service import ParameterService


class ProjectSynchronizer:
    @staticmethod
    def synchronize_project(scene: bpy.types.Scene) -> None:

        project = scene.ubk_project
        runtime = RuntimeManager.get(scene)
        image_preview = runtime.image_preview
        artifacts = runtime.artifacts
        artifacts.rebuild()
        for bake_group in project.bake_groups:
            for baker in bake_group.bakers:
                if baker.accumulated_image is not None:
                    LOG.debug(f"Updating Preview for {baker.accumulated_image.name}")
                    image_preview.update(baker.accumulated_image, baker.accumulated_producer_uuid)

                LOG.debug(f"Synchronize parameter for baker : {baker.baker}")
                definition = registry_definition.get(baker.baker)

                if definition is None:
                    LOG.debug("Definition not Found")
                    continue

                if isinstance(definition, CustomBakerDefinition):
                    baker_producer = registry_baker[baker.baker]
                    baker_producer.bake_colorspace = ImageColorSpace(definition.bake_colorspace)
                    baker_producer.image_colorspace = ImageColorSpace(definition.image_colorspace)
                    baker_producer.color_management_info = ColorManagementInfo(
                        display_device=DisplayDevice(definition.display_device),
                        view_transform=ViewTransform(definition.view_transform),
                        look=definition.look,
                        exposure=definition.exposure,
                        gamma=definition.gamma,
                    )

                ParameterService.synchronize(definition, baker.custom_baker)

    @classmethod
    def synchronize_current_project(cls):
        cls.synchronize_project(bpy.context.scene)

    @classmethod
    def synchronize_blend_file(cls):
        for scene in bpy.data.scenes:
            cls.synchronize_project(scene)
