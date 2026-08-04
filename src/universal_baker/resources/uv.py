from __future__ import annotations

from dataclasses import dataclass

from ..enum.image_layout import ImageLayout


@dataclass(frozen=True)
class UVLayout:
    image_layout: ImageLayout
    udim_tiles: tuple[tuple[int, int], ...]
