from __future__ import annotations


from .label_set import LabelSet
from .tile_set import TileSet
from ..resources.image_buffer import ImageBuffer
from ..resources.label_buffer import LabelBuffer


class ImageMask:
    """Transient ownership mask."""

    def __init__(
        self,
        tiles: TileSet,
        name: str = "Mask",
        labels: LabelSet | None = None,
    ):
        self.name = name
        self.tiles = tiles
        self.labels = labels

    @property
    def tile_numbers(self) -> tuple[int, ...]:
        return self.tiles.tiles

    def get_tile(self, tile: int) -> ImageBuffer:
        return self.tiles[tile]

    def get_label(self, tile: int) -> LabelBuffer | None:
        if self.labels is None:
            return None

        return self.labels[tile]
