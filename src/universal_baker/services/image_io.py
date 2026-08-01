from __future__ import annotations
from pathlib import Path

import bpy
from universal_baker.constant import LOG

from ..resources.image import ImageResource
from ..runtime.image_buffer import ImageBuffer
from .image_base import ImageServiceBase

LOG_SCOPE = "Image IO"


class ImageIOService(ImageServiceBase):
    """Service to convert Images to ImageBuffers and vice versa"""

    @staticmethod
    def read_image(image: bpy.types.Image) -> ImageBuffer:
        """Convert ImageResource to ImageBuffer for manipulation"""
        with LOG.scope(LOG_SCOPE):
            LOG.info(f'Create Buffer from Image "{image.name}"')
            buffer = ImageBuffer.from_blender_image(image)

            return buffer

    @classmethod
    def read(cls, resource: ImageResource) -> ImageBuffer:
        """Convert ImageResource to ImageBuffer for manipulation"""
        with LOG.scope(LOG_SCOPE):
            LOG.info(f'Create Buffer from Image Resource "{resource.name}"')
            image = resource.image

            if image is None:
                image = cls.create(resource)

            return cls.read_image(image)

    @staticmethod
    def write(resource: ImageResource, buffer: ImageBuffer) -> None:
        """Write buffer to Image"""
        with LOG.scope(LOG_SCOPE):
            LOG.info(f'Write Buffer "{buffer.name}" to Image "{resource.name}"')

            image = resource.image
            assert image is not None

            if image.size[0] != resource.width or image.size[1] != resource.height:
                image.scale(buffer.width, buffer.height)

            buffer.write_to_blender_image(image)
            image.update()

    @staticmethod
    def validate_channels(): ...

    @staticmethod
    def load(path: Path) -> bpy.types.Image:
        return bpy.data.images.load(str(path))
