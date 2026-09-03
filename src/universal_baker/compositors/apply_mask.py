from __future__ import annotations

from .base import Compositor
from ..resources.image_buffer import ImageBuffer
from ..core.registry_compositor import registry_compositor


class CompositeApplyMask(Compositor):
    id: str = "APPLY_MASK"
    name: str = "Apply Mask"
    description: str = "Mask the buffer with the alpha channel of the input image"

    def composite(self, buffer: ImageBuffer, image: ImageBuffer) -> None:
        """Composite Image to buffer"""
        super().composite(buffer, image)

        alpha = image.pixels[..., 3:4]

        # Alpha composite :
        buffer.pixels[..., 3] = alpha[..., 0] * buffer.pixels[..., 3]


classes = (CompositeApplyMask,)


def register():
    for c in classes:
        registry_compositor.register(c())


def unregister():
    for c in classes:
        registry_compositor.unregister(c.id)
