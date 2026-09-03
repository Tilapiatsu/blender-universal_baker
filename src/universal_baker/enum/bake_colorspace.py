from __future__ import annotations

from enum import Enum, auto


class BakeColorSpace(Enum):
    COLOR = "COLOR"
    NON_COLOR = "NON_COLOR"


class BakerColorType(Enum):
    COLOR = auto()
    DATA = auto()
    MASK = auto()
    VECTOR = auto()
