from __future__ import annotations

from enum import Enum


class Channel(str, Enum):
    R = "R"
    G = "G"
    B = "B"
    A = "A"


CHANNEL_ITEMS = [
    (Channel.R.value, Channel.R.value, ""),
    (Channel.G.value, Channel.G.value, ""),
    (Channel.B.value, Channel.B.value, ""),
    (Channel.A.value, Channel.A.value, ""),
]
