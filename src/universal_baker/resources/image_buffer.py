from __future__ import annotations

import numpy as np
import bpy
from ..constant import LOG

from dataclasses import dataclass


@dataclass(slots=True)
class ImageBuffer:
    """
    Raw Pixel manipulation used to pack images differently

    Represents raw pixel data for a single tile and is the only object compositors and packers need to manipulate.
    """

    width: int
    height: int

    pixels: np.ndarray

    channels: int = 4
    name: str = ""

    @property
    def size(self) -> int:
        """Returns the number of pixels in an buffer"""
        return self.width * self.height

    @property
    def flat_pixels(self) -> np.ndarray:
        return self.pixels.reshape(-1)

    @property
    def is_float(self) -> bool:
        # TODO : To be written
        return False

    @classmethod
    def empty(cls, width: int, height: int, channels: int = 4, name: str = "Image") -> ImageBuffer:
        """Create an Empty Buffer"""

        pixels = np.zeros((width, height, channels), dtype=np.float32)

        return cls(width, height, pixels, channels=channels, name=name)

    @classmethod
    def from_blender_image(cls, image: bpy.types.Image) -> ImageBuffer:
        """Create an Empty Buffer"""

        buffer = cls.empty(image.size[0], image.size[1], channels=4, name=image.name)
        image.pixels.foreach_get(buffer.flat_pixels)

        return buffer

    @classmethod
    def copy(cls): ...

    @classmethod
    def fill(cls): ...

    @classmethod
    def clear(cls): ...

    def write_to_blender_image(self, image: bpy.types.Image) -> None:
        image.pixels.foreach_set(self.flat_pixels)

    def reshape(self) -> np.ndarray:
        return np.reshape(self.pixels, (self.height, self.width, self.channels))

    def is_empty(self) -> bool:
        if np is not None:
            result = np.greater(self.pixels, 0)
            for r in result:
                if r.all():
                    return False
            return True
        return True

    @classmethod
    def clone(cls): ...
