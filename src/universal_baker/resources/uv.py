from __future__ import annotations

from dataclasses import dataclass

from ..enum.image_layout import ImageLayout
from ..services.uv import UVService


@dataclass(frozen=True)
class UVLayout:
    image_layout: ImageLayout
    udim_tiles: tuple[tuple[int, int], ...]

    @property
    def tiles(self) -> tuple[int, ...]:
        return tuple(UVService.tile_numbers(self.udim_tiles))
