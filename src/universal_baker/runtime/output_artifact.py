from __future__ import annotations

import bpy
from uuid import uuid4

from pathlib import Path
from typing import TYPE_CHECKING


from ..constant import LOG
from ..resources.image import ImageResource
from ..enum.channels import Channel
from ..runtime.bake_group import BakeGroup
from ..runtime.output_base import OutputBase
from ..services.image_io import ImageIOService

if TYPE_CHECKING:
    from bpy.types import Scene
    from ..properties.artifact import UBK_Artifact


class OutputArtifact(OutputBase):
    uuid: str
    dependencies: list[str]
    dependency_mapping: list[Channel]

    def __init__(self, scene: Scene, property_group: UBK_Artifact):
        self.scene = scene
        self.data = property_group
        self.name = self.data.name
        self.bake_group = BakeGroup(self.data.bake_group_uuid)
        self.uuid = str(uuid4())
        self.dependencies = []
        self.dependency_mapping = []

        for d in property_group.dependencies:
            self.dependencies.append(d.uuid)

        for m in property_group.dependencies_mapping:
            self.dependency_mapping.append(m)

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
    def target_object_uuid(self) -> str:
        return self.data.target_object_uuid

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
        Returns an ImageResource.
        """
        LOG.debug(f"Loading Image {self.name}")
        image = bpy.data.images.get(self.name)
        if image is None:
            image = ImageIOService.load(self.path)
        return ImageIOService.init_resource(image)
