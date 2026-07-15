from __future__ import annotations

from enum import Enum


class Channel(str, Enum):
    R = "R"
    G = "G"
    B = "B"
    A = "A"
    RGB = "RGB"


CHANNEL_ITEMS = [
    (Channel.R.value, "Red", ""),
    (Channel.G.value, "Green", ""),
    (Channel.B.value, "Blue", ""),
    (Channel.A.value, "Alpha", ""),
    (Channel.RGB.value, "RGB", ""),
]
