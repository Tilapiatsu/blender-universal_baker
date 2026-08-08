from __future__ import annotations

from dataclasses import dataclass

from .tile_set import TileSet

from .bake_group import BakeGroup


@dataclass(slots=True)
class OutputBase:
    uuid: str
    name: str
    tiles: TileSet
    bake_group: BakeGroup
