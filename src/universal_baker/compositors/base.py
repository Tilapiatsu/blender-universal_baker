from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from ..runtime.image_buffer import ImageBuffer


class Compositor(ABC):
    id: str
    name: str
    description: str
    icon: str

    @abstractmethod
    def composite(self, buffer: ImageBuffer, image: ImageBuffer) -> None:
        """Composite Image to buffer"""
        reshape_buffer = False
        reshape_image = False

        if buffer.width != image.width:
            if buffer.width > image.width:
                image.width = buffer.width
                reshape_image = True
            else:
                buffer.width = image.width
                reshape_buffer = True

        if buffer.height != image.height:
            if buffer.height > image.height:
                image.height = buffer.height
                reshape_image = True
            else:
                buffer.height = image.height
                reshape_buffer = True

        if reshape_buffer:
            buffer.reshape()

        if reshape_image:
            image.reshape()
