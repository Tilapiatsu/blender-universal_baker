from __future__ import annotations
from pathlib import Path

import bpy
from universal_baker.constant import LOG

from ..resources.image import ImageResource
from ..runtime.image_buffer import ImageBuffer
from .image_base import ImageServiceBase

LOG_SCOPE = "Image IO Service"


class ImageIOService(ImageServiceBase):
    """Service to convert Images to ImageBuffers and vice versa"""

    @staticmethod
    def read(resource: ImageResource) -> ImageBuffer:
        """Convert Image to ImageBuffer for manipulation"""
        with LOG.scope(LOG_SCOPE):
            LOG.info(f'Create Buffer from Image Resource "{resource.name}"')
            image = resource.image
            assert image is not None

            width = image.size[0]
            height = image.size[1]

            buffer = ImageBuffer.empty(width, height, image.name)

            image.pixels.foreach_get(buffer.pixels)

            return buffer

    @staticmethod
    def write(resource: ImageResource, buffer: ImageBuffer) -> None:
        """Save buffer to Image"""
        with LOG.scope(LOG_SCOPE):
            LOG.info(f'Write Buffer "{buffer.name}" to Image Resource "{resource.name}"')

            image = resource.image
            assert image is not None

            if image.size[0] != resource.width or image.size[1] != resource.height:
                image.scale(buffer.width, buffer.height)

            image.pixels.foreach_set(buffer.pixels)
            image.update()

    @staticmethod
    def validate_channels(): ...

    @staticmethod
    def load(path: Path) -> bpy.types.Image:
        bpy.data.images.load(path)
