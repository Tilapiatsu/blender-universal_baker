from __future__ import annotations

from pathlib import Path

import bpy

from universal_baker.runtime.settings_image import ColorManagementSettings

from ..constant import LOG
from ..resources.image import ImageResource
from ..resources.image_buffer import ImageBuffer
from ..runtime.output_artifact import OutputArtifact
from ..runtime.tile_set import TileSet
from .image_base import ImageServiceBase

LOG_SCOPE = "Image IO"


class ImageIOService(ImageServiceBase):
    """Service to convert Images to ImageBuffers and vice versa"""

    @staticmethod
    def read_image(image: bpy.types.Image) -> ImageBuffer:
        """Convert ImageResource to ImageBuffer for manipulation"""
        with LOG.scope(LOG_SCOPE):
            LOG.debug(f'Create Buffer from Image "{image.name}"')
            buffer = ImageBuffer.from_blender_image(image)

            return buffer

    @classmethod
    def read(cls, resource: ImageResource) -> ImageBuffer:
        """Convert ImageResource to ImageBuffer for manipulation"""
        with LOG.scope(LOG_SCOPE):
            LOG.debug(f'Create Buffer from Image Resource "{resource.name}"')
            image = resource.image

            if image is None:
                image = cls.create(resource)

            return cls.read_image(image)

    @classmethod
    def export_tiles(cls, artifact: OutputArtifact, tiles: TileSet) -> None:
        for tile in tiles.keys():
            artifact.image.tile_path(tile)

    @classmethod
    def import_tiles(cls, artifact: OutputArtifact) -> None: ...

    @staticmethod
    def validate_channels(): ...

    @staticmethod
    def load(path: Path, colorspace_settings: ColorManagementSettings, is_udim: bool = False) -> bpy.types.Image:
        with LOG.scope(LOG_SCOPE):
            LOG.debug(f"Loading image : {str(path)}")
            image = bpy.data.images.load(str(path))
            image.colorspace_settings.name = colorspace_settings.colorspace
            image.use_view_as_render = True

            image.name = image.name.split(".")[0]

            if is_udim:
                image.source = "TILED"
            return image
