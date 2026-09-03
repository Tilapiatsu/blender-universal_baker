from __future__ import annotations

from enum import StrEnum


class ImageColorSpace(StrEnum):
    SRGB = "sRGB"
    NON_COLOR = "Non-Color"
    ACES_2_0 = "ACES 2.0 sRGB"
    REC_2020 = "Rec.2020"
