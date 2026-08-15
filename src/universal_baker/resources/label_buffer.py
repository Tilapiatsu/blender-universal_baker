from __future__ import annotations

import numpy as np
from ..constant import LOG

from dataclasses import dataclass


@dataclass(slots=True)
class LabelBuffer:
    """
    Raw Pixel Label,

    Allow to Identify a pixel with a label. Useful to mask part of a buffer and defines ownership
    """

    width: int
    height: int

    pixels: np.ndarray

    name: str = ""

    @property
    def size(self) -> int:
        """Returns the number of pixels in an buffer"""
        return self.width * self.height

    @property
    def flat_pixels(self) -> np.ndarray:
        return self.pixels.reshape(-1)

    @property
    def shape(self) -> tuple[int, int]:
        return (
            self.width,
            self.height,
        )

    @classmethod
    def empty(cls, width: int, height: int, name: str = "Image") -> LabelBuffer:
        """Create an Empty Buffer"""
        pixels = np.zeros((width, height), dtype=np.uint32)

        return cls(width, height, pixels, name=name)

    @classmethod
    def copy(cls): ...

    @classmethod
    def fill(cls): ...

    @classmethod
    def clear(cls): ...

    def reshape(self) -> np.ndarray:
        return np.reshape(self.pixels, (self.height, self.width))

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
