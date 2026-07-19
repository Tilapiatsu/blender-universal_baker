from __future__ import annotations

import bpy

from ..ressources.image import ImageResource
from ..runtime.image_buffer import ImageBuffer
from .image_base import ImageServiceBase


class ImageIOService:
    """Service to convert Images to ImageBuffers and vice versa"""

    @staticmethod
    def read(image: bpy.types.Image) -> ImageBuffer:
        """Convert Image to ImageBuffer for manipulation"""
        width = image.size[0]
        height = image.size[1]

        buffer = ImageBuffer.empty(width, height)

        image.pixels.foreach_get(buffer.pixels)

        return buffer

    @staticmethod
    def write(image: bpy.types.Image, buffer: ImageBuffer) -> None:
        """Save buffer to Image"""
        image.scale(buffer.width, buffer.height)
        image.pixels.foreach_set(buffer.pixels)
        image.update()

    @staticmethod
    def ensure_image_sizes(*resources: ImageResource):
        ImageServiceBase.ensure_image_sizes(*resources)

    @staticmethod
    def validate_channels(): ...
