from __future__ import annotations


from ..constant import LOG
from ..runtime.image_buffer import ImageBuffer
from ..compositors.base import Compositor


class ImageAccumulator:
    def __init__(self, width, height, name: str = "Image"):
        self._buffer = ImageBuffer.empty(width, height, name=name)

    def accumulate(self, image: ImageBuffer, compositor: Compositor) -> None:
        """Accumulate Image to buffer"""
        LOG.info(f"Accumulate image : {image.name}")
        compositor.composite(self._buffer, image)

    def result(self) -> ImageBuffer:
        """Returns Accumulated buffer"""
        return self._buffer
