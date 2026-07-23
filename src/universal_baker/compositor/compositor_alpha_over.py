from __future__ import annotations

from .compositor import Compositor
from ..runtime.image_buffer import ImageBuffer


class CompositeAlphaOver(Compositor):
    def composite(self, buffer: ImageBuffer, image: ImageBuffer) -> None:
        """Composite Image to buffer"""
        super().composite(buffer, image)

        alpha = image.pixels[..., 3:4]
        # RGB composite :
        buffer.pixels[..., 0:3] = image.pixels[..., 0:3] * alpha + buffer.pixels[..., 0:3] * (1 - alpha)

        # Alpha composite :
        buffer.pixels[..., 3] = alpha[..., 0] + buffer.pixels[..., 3] * (1 - alpha[..., 0])
