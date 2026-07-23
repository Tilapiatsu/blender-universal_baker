from __future__ import annotations

from ..runtime.image_buffer import ImageBuffer
from ..compositor.compositor import Compositor


class ImageAccumulator:
    def __init__(self, width, height):
        self._buffer = ImageBuffer.empty(width, height)

    def accumulate(self, image: ImageBuffer, compositor: Compositor) -> None:
        """Accumulate Image to buffer"""
        compositor.composite(self._buffer, image)

    def result(self) -> ImageBuffer:
        """Returns Accumulated buffer"""
        return self._buffer
