from __future__ import annotations

from dataclasses import dataclass
import array

try:
    import numpy as np
except ImportError:
    np = None


@dataclass(slots=True)
class ImageBuffer:
    """Raw Pixel manipulation used to pack images differently"""

    width: int
    height: int

    pixels: array | np.array

    channels: int = 4

    @property
    def size(self):
        """Returns the number of pixels in an buffer"""
        return self.width * self.height

    @classmethod
    def empty(cls, width: int, height: int):
        """Create an Empty Buffer"""
        length = width * height * 4

        if np is not None:
            pixels = np.zeros(length, dtype=np.float32)

        else:
            pixels = array.array("f", [0.0] * length)

        return cls(width, height, pixels)

    @classmethod
    def copy(cls): ...

    @classmethod
    def fill(cls): ...

    @classmethod
    def clear(cls): ...

    @classmethod
    def reshape(self):

        if np is None:
            raise RuntimeError("NumPy unavailable.")

        return self.pixels.reshape((self.height, self.width, 4))

    @classmethod
    def clone(cls): ...
