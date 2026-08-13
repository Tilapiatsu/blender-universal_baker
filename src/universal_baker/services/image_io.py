from __future__ import annotations
from pathlib import Path

import bpy

from ..constant import LOG
from ..runtime.output_artifact import OutputArtifact
from ..runtime.tile_set import TileSet

from ..resources.image import ImageResource
from ..resources.image_buffer import ImageBuffer
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
    def write(cls, resource: ImageResource, tiles: TileSet) -> None:
        """Write buffer to Image"""
        with LOG.scope(LOG_SCOPE):
            if not tiles.is_udim and not resource.is_udim:
                buffer = tiles.base_buffer
                assert buffer is not None
                if buffer.dirty:
                    return
                cls.write_single(resource, buffer.buffer)

            elif tiles.is_udim and resource.is_udim:
                cls.write_udim(resource, tiles)

            else:
                LOG.error("Buffer and Image have to be compatible : Both using UDIM or both being single image.")

    @staticmethod
    def write_single(resource: ImageResource, buffer: ImageBuffer) -> None:
        LOG.debug(f'Write Buffer "{buffer.name}" to Image "{resource.name}"')

        image = resource.image
        assert image is not None

        if image.size[0] != resource.width or image.size[1] != resource.height:
            image.scale(buffer.width, buffer.height)

        buffer.write_to_blender_image(image)
        image.update()

    @staticmethod
    def write_udim(resource: ImageResource, tiles: TileSet) -> None:
        for udim, buffer in tiles.items():
            pass

    @classmethod
    def export_tiles(cls, artifact: OutputArtifact, tiles: TileSet) -> None:
        for tile in tiles.keys():
            filepath = artifact.image.tile_path(tile)

    @classmethod
    def import_tiles(cls, artifact: OutputArtifact) -> None: ...

    @staticmethod
    def validate_channels(): ...

    @staticmethod
    def load(path: Path, is_udim: bool = False) -> bpy.types.Image:
        with LOG.scope(LOG_SCOPE):
            LOG.debug(f"Loading image : {str(path)}")
            image = bpy.data.images.load(str(path))
            if is_udim:
                image.source = "TILED"
            return image
