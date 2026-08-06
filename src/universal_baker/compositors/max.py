from __future__ import annotations

import numpy as np

from .base import Compositor
from ..resources.image_buffer import ImageBuffer
from ..core.registry_compositor import registry_compositor


class CompositeMax(Compositor):
    id: str = "MAX"
    name: str = "Maximum"
    description: str = "Composite image over the buffer using the image alpha"

    def composite(self, buffer: ImageBuffer, image: ImageBuffer) -> None:
        """Composite Image to buffer"""
        super().composite(buffer, image)

        buffer.pixels[..., 0:3] = np.maximum(
            buffer.pixels[..., 0:3],
            image.pixels[..., 0:3],
        )

        buffer.pixels[..., 3] = 1.0


classes = (CompositeMax,)


def register():
    for c in classes:
        registry_compositor.register(c())


def unregister():
    pass
