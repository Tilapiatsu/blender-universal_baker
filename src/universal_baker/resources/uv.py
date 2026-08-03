from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UVLayout:
    uv_layer: str
    use_udim: bool
    udim_tiles: tuple[tuple[int, int], ...]
