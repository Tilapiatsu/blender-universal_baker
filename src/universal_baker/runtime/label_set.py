from __future__ import annotations
from dataclasses import dataclass

import bpy

from typing import Iterable


from .settings_output import OutputSettings
from ..resources.label_buffer import LabelBuffer


@dataclass(slots=True)
class LabelData:
    buffer: LabelBuffer
    dirty: bool = True


class LabelSet:
    """Representation of label buffer per UDIM Tile.
    If the image is not a UDIM, only one buffer is stored at indices 1001"""

    _labels: dict[int, LabelData]

    def __init__(self):
        self._labels: dict[int, LabelData] = {}

    @property
    def numbers(self) -> Iterable[int]:
        return iter(self.keys())

    @property
    def tiles(self) -> tuple[int, ...]:
        return tuple(self._labels.keys())

    @property
    def is_udim(self) -> bool:
        return not (len(self._labels) == 1 and 1001 in self.keys())

    @property
    def base_buffer(self) -> LabelData | None:
        if self.is_udim:
            return

        return self._labels[1001]

    @property
    def tile_buffers(self) -> list[tuple[int, LabelBuffer]]:
        return [(tile, buffer.buffer) for tile, buffer in self.items()]

    @property
    def buffers(self) -> list[LabelBuffer]:
        return [t.buffer for t in self._labels.values()]

    @property
    def dirty_buffers(self) -> list[LabelBuffer]:
        return [t.buffer for t in self._labels.values() if t.dirty]

    @property
    def is_empty(self) -> bool:
        return len(self._labels) == 0

    @property
    def is_dirty(self) -> bool:
        return len(self.dirty_buffers) > 0

    def add_tile(self, tile: int, buffer: LabelBuffer, override: bool = False) -> None:
        if not override and tile in self.keys():
            return
        td = LabelData(buffer)
        self._labels[tile] = td

    def add_empty_tile(
        self,
        tile: int,
        resolution: tuple[int, int],
        name: str = "Tile",
        override: bool = False,
    ) -> None:
        if not override and tile in self.keys():
            return
        empty_buffer = LabelBuffer.empty(
            width=resolution[0],
            height=resolution[1],
            name=name,
        )
        td = LabelData(empty_buffer)
        self._labels[tile] = td

    def set_labelset(self, labelset: LabelSet, clear: bool = False, override: bool = False) -> None:
        if clear:
            self.clear()
        for tile, tile_data in labelset.tile_buffers:
            self.add_tile(tile, tile_data, override=override)

    def clear(self) -> None:
        self._labels = {}

    def set_dirty(self, key: int, value: bool) -> None:
        if key not in self._labels:
            return

        self._labels[key].dirty = value

    def overlaps(self, labelset: LabelSet) -> bool:
        for tile in labelset.keys():
            if tile not in self._labels.keys():
                return False
        return True

    def contains(self, labelset: LabelSet) -> bool:
        contains = False
        for tile in labelset.keys():
            if tile in self._labels.keys():
                return True

        return contains

    def __contains__(self, key: int) -> bool:
        return key in self._labels

    def keys(self):
        return list(self._labels.keys())

    def values(self):
        values = [t.buffer for t in self._labels.values()]
        return values

    def update(self, *args, **kwargs):
        return self._labels.update(*args, **kwargs)

    def items(self):
        return self._labels.items()

    def __setitem__(self, key: int, item: LabelBuffer):
        td = LabelData(item)
        self._labels[key] = td

    def __getitem__(self, key: int) -> LabelBuffer:
        td = self._labels[key]
        if td is None:
            return td
        return td.buffer

    def __repr__(self) -> str:
        return repr(self._labels)

    def __len__(self) -> int:
        return len(self._labels)

    def __delitem__(self, key: int) -> None:
        del self._labels[key]
