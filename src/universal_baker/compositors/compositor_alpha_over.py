from __future__ import annotations

from .compositor import Compositor
from ..runtime.image_buffer import ImageBuffer
from ..core.registry_compositor import registry_compositor


class CompositeAlphaOver(Compositor):
    id: str = "ALPHA_OVER"
    name: str = "Alpha Over"
    description: str = "Composite image over the buffer using the image alpha"

    def composite(self, buffer: ImageBuffer, image: ImageBuffer) -> None:
        """Composite Image to buffer"""
        super().composite(buffer, image)

        alpha = image.pixels[..., 3:4]
        # RGB composite :
        buffer.pixels[..., 0:3] = image.pixels[..., 0:3] * alpha + buffer.pixels[..., 0:3] * (1 - alpha)

        # Alpha composite :
        buffer.pixels[..., 3] = alpha[..., 0] + buffer.pixels[..., 3] * (1 - alpha[..., 0])


classes = (CompositeAlphaOver,)


def register():
    for c in classes:
        registry_compositor.register(c())


def unregister():
    pass
