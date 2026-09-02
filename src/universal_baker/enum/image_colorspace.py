from __future__ import annotations

from enum import Enum


class ImageColorSpace(Enum):
    SRGB = "sRGB"
    NON_COLOR = "Non-Color"
    ACES_2_0 = "ACES 2.0 sRGB"
    REC_2020 = "Linear CIE-XYZ D65"
