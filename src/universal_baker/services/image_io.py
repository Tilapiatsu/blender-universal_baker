from __future__ import annotations

import bpy

from ..resources.image import ImageResource
from ..runtime.image_buffer import ImageBuffer
from .image_base import ImageServiceBase


class ImageIOService(ImageServiceBase):
    """Service to convert Images to ImageBuffers and vice versa"""

    @staticmethod
    def read(resource: ImageResource) -> ImageBuffer:
        """Convert Image to ImageBuffer for manipulation"""
        image = resource.image
        assert image is not None

        width = image.size[0]
        height = image.size[1]

        buffer = ImageBuffer.empty(width, height)

        image.pixels.foreach_get(buffer.pixels)

        return buffer

    @staticmethod
    def write(resource: ImageResource, buffer: ImageBuffer) -> None:
        """Save buffer to Image"""
        image = resource.image
        assert image is not None

        if image.width != resource.width or image.height != resource.height:
            image.scale(buffer.width, buffer.height)

        image.pixels.foreach_set(buffer.pixels)
        image.update()

    @staticmethod
    def validate_channels(): ...
