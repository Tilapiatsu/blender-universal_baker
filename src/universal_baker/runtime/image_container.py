from __future__ import annotations


from ..resources.image_buffer import ImageBuffer
from .tile_set import TileSet


class ImageContainer:
    """Transient pixel ownership Image."""

    def __init__(self, tiles: TileSet, name: str = "Mask"):
        self.name = name
        self.tiles = tiles

    def tile(self, tile: int) -> ImageBuffer | None:
        if tile not in self.tiles:
            return
        return self.tiles[tile].buffer

    @property
    def tile_numbers(self) -> tuple[int, ...]:
        return tuple(self.tiles.numbers)
