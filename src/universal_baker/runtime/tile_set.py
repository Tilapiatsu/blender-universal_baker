from __future__ import annotations
from dataclasses import dataclass

import bpy

from typing import Iterable

from ..resources.image_buffer import ImageBuffer


@dataclass(slots=True)
class TileData:
    buffer: ImageBuffer
    dirty: bool = True


class TileSet:
    """Representation of image buffer per UDIM Tile.
    If the image is not a UDIM, only one buffer is stored at indices 1001"""

    _tiles: dict[int, TileData]

    def __init__(self):
        self._tiles: dict[int, TileData] = {}

    @classmethod
    def from_blender_image(cls, image: bpy.types.Image) -> TileSet:
        from ..services.image_io import ImageIOService

        ts = TileSet()

        if image.tiles is None:
            ts[1001] = TileData(buffer=ImageBuffer.from_blender_image(image))
            return ts

        for t in image.tiles.values():
            tile_image = ImageIOService.load(image.filepath_raw.replace("<UDIM>", str(t.number)))
            ts[t.number] = TileData(ImageBuffer.from_blender_image(tile_image))

            bpy.data.images.remove(tile_image)

        return ts

    @property
    def numbers(self) -> Iterable[int]:
        return iter(self.keys())

    # @property
    # def is_udim(self) -> bool:
    #     return len(self._tiles) != 0 and (len(self._tiles) > 1 or 1001 not in self.keys())

    @property
    def is_udim(self) -> bool:
        return not (len(self._tiles) == 1 and 1001 in self.keys())

    @property
    def base_buffer(self) -> TileData | None:
        if self.is_udim:
            return

        return self._tiles[1001]

    @property
    def tile_buffers(self) -> list[tuple[int, ImageBuffer]]:
        return [(tile, buffer.buffer) for tile, buffer in self.items()]

    @property
    def buffers(self) -> list[ImageBuffer]:
        return [t.buffer for t in self.values()]

    @property
    def dirty_buffers(self) -> list[ImageBuffer]:
        return [t.buffer for t in self.values() if t.dirty]

    @property
    def is_empty(self) -> bool:
        return len(self._tiles) == 0

    def clear(self) -> None:
        self._tiles = {}

    def set_dirty(self, key: int, value: bool) -> None:
        if key not in self._tiles:
            return

        self._tiles[key].dirty = value

    def __contains__(self, key: int) -> bool:
        return key in self._tiles.keys()

    def keys(self):
        return list(self._tiles.keys())

    def values(self):
        return list(self._tiles.values())

    def update(self, *args, **kwargs):
        return self._tiles.update(*args, **kwargs)

    def items(self):
        return self._tiles.items()

    def __setitem__(self, key: int, item: TileData):
        item.dirty = True
        self._tiles[key] = item

    def __getitem__(self, key: int) -> TileData:
        return self._tiles[key]

    def __repr__(self) -> str:
        return repr(self._tiles)

    def __len__(self) -> int:
        return len(self._tiles)

    def __delitem__(self, key: int) -> None:
        del self._tiles[key]
