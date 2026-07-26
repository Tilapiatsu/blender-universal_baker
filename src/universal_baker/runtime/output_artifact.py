from __future__ import annotations

import bpy

from pathlib import Path
from typing import TYPE_CHECKING

from ..core.controller import BakeController

from .bake_group import BakeGroup

from ..resources.image import ImageResource

from .output_base import OutputBase
from .output_bake import OutputBake
from .output_accumulated import OutputAccumulated
from .output_pack import OutputPack
from ..services.image_io import ImageIOService

if TYPE_CHECKING:
    from bpy.types import Scene
    from ..properties.artifact import UBK_Artifact


class OutputArtifact:
    uuid: str
    bake_group_uuid: str
    producer_uuid: str

    def __init__(self, scene: Scene, property_group: UBK_Artifact):
        self.scene = scene
        self.data = property_group
        self.bake_group_uuid = property_group.bake_group_uuid
        self.producer_uuid = property_group.producer_uuid

    @property
    def path(self) -> Path:
        return Path(bpy.path.abspath(self.data.relative_path))

    def exists(self) -> bool:
        return self.path.exists()

    def load_image(self) -> ImageResource:
        """
        Returns an ImageBuffer.
        """
        image = ImageIOService.load(self.path)

        return ImageIOService.init_resource(image)

    def create_output(self) -> OutputBase:
        """
        Materializes this artifact into
        a runtime OutputBase.
        """

        image = self.load_image()
        image_buffer = ImageIOService.read(image)
        # TODO: Implement Output for all archetype types
        match self.data.type:
            case "BAKE":
                output = OutputBake(
                    uuid=self.data.uuid,
                    bake_group=self.data.bake_group_uuid,
                    target_object=self.data.target_object[0],
                    baker=self.data.producer_uuid,
                    image=image_buffer,
                )
            case "ACCUMULATED":
                output_bakes = []
                for b in self.data.dependencies:
                    baker = BakeController.get_baker_from_uuid(b.artifact_uuid)
                    if baker is None:
                        continue

                    output_bakes.append(baker)

                output = OutputAccumulated(
                    uuid=self.data.uuid,
                    image=image_buffer,
                    baker=self.data.baker_uuid,
                    bake_group=BakeGroup(self.data.bake_group_uuid),
                    target_objects=self.data.target_objects,
                    output_bakes=output_bakes,
                )
            case "PACK":
                pass
            case _:
                pass

        output.uuid = self.uuid

        return output
