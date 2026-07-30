from __future__ import annotations

import bpy

from pathlib import Path
from typing import TYPE_CHECKING

from ..packers.channels import Channel

from ..resources.image import ImageResource

from ..services.image_io import ImageIOService

if TYPE_CHECKING:
    from bpy.types import Scene
    from ..properties.artifact import UBK_Artifact


class OutputArtifact:
    uuid: str
    dependencies: list[str]
    dependency_mapping: list[Channel]

    def __init__(self, scene: Scene, property_group: UBK_Artifact):
        self.scene = scene
        self.data = property_group
        self.dependencies = []
        self.dependency_mapping = []

        for d in property_group.dependencies:
            self.dependencies.append(d.uuid)

        for m in property_group.dependency_mapping:
            self.dependency_mapping.append(m)

    @property
    def name(self) -> str:
        return self.data.name

    @property
    def type(self) -> str:
        return self.data.type

    @property
    def bake_group_uuid(self) -> str:
        return self.data.bake_group_uuid

    @property
    def producer_uuid(self) -> str:
        return self.data.producer_uuid

    @property
    def target_object(self) -> bpy.types.Object:
        return self.data.producer_uuid

    @property
    def path(self) -> Path:
        """Returns the resolved path  of the file"""
        return Path(bpy.path.abspath(self.data.relative_path))

    def exists(self) -> bool:
        """Returns true if the file exists on disk"""
        return self.path.exists()

    def load_image(self) -> ImageResource:
        """
        Returns an ImageBuffer.
        """
        image = ImageIOService.load(self.path)

        return ImageIOService.init_resource(image)
