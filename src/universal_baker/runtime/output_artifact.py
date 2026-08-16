from __future__ import annotations

import bpy

from pathlib import Path
from typing import TYPE_CHECKING

from .tile_set import TileSet

from ..constant import LOG
from ..resources.image import ImageResource
from ..enum.channels import Channel
from ..runtime.bake_group import BakeGroup
from .logical_image import LogicalImage

if TYPE_CHECKING:
    from .settings_output import OutputSettings
    from bpy.types import Scene
    from ..properties.artifact import UBK_Artifact


class OutputArtifact:
    uuid: str
    dependencies: list[str]
    dependency_mapping: list[Channel]
    image: LogicalImage
    output_settings: OutputSettings

    def __init__(self, scene: Scene, property_group: UBK_Artifact):
        udim_tiles = property_group.get_udim_tiles()
        # ISSUE: udim_tiles arrive empty for some reason, because the artifact is created with no tiles ?
        print(udim_tiles)
        self.image = LogicalImage.create(
            layout=property_group.image_layout,
            path=property_group.absolute_path,
            tiles=udim_tiles,
        )
        self.scene = scene
        self.data = property_group
        self.output_settings: OutputSettings = property_group.get_output_settings()
        self.name = self.data.name
        self.bake_group = BakeGroup(self.data.bake_group_uuid)
        self.uuid = property_group.uuid
        self.dependencies = []
        self.dependency_mapping = []

        for d in property_group.dependencies:
            self.dependencies.append(d.uuid)

        for m in property_group.dependencies_mapping:
            self.dependency_mapping.append(m)

    @property
    def is_udim(self) -> bool:
        return self.image.is_udim

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
        return self.image.path

    def exists(self) -> bool:
        """Returns true if the file exists on disk"""
        return self.image.exists

    def load_image(self) -> ImageResource:
        """
        Returns an ImageResource.
        """
        from ..services.image_io import ImageIOService

        image = bpy.data.images.get(self.name)

        if image is None:
            LOG.debug(f"Loading Image {self.name}")
            image = ImageIOService.load(self.path, self.image.is_udim)

        return ImageIOService.init_resource(image, self.output_settings)

    def init_empty_image(self) -> None:
        from ..services.image_codec import ImageCodec

        LOG.debug("Init Empty image files for Artrifact")
        tileset = TileSet()
        for t in self.image.tiles:
            tileset.add_empty_tile(
                t,
                (
                    self.output_settings.path.width,
                    self.output_settings.path.height,
                ),
            )

        ImageCodec.export_tiles(self, tileset, self.output_settings)

    def __repr__(self) -> str:
        result = f"{self.uuid} | {self.image}"
        return result
