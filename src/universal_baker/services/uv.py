from __future__ import annotations

import math

from ..constant import LOG


class UVService:
    @staticmethod
    def detect_udim_tiles(obj, uv_name) -> tuple:
        tiles = set()

        mesh = obj.data

        if mesh is None:
            LOG.critical(f"Object {obj.name} doesn't have data", display_in_ui=True)
            return tuple(tiles)

        uv_layer = obj.data.uv_layers.get(uv_name)

        if uv_layer is None:
            LOG.critical(f"Object {obj.name} doesn't have uv named {uv_name}", display_in_ui=True)
            return tuple(tiles)

        for loop in mesh.loops:
            uv = uv_layer.data[loop.index].uv

            tile = (
                math.floor(uv.x),
                math.floor(uv.y),
            )

            tiles.add(tile)

        return tuple(tiles)

    @staticmethod
    def tile_number(x, y) -> int:
        return 1001 + x + y * 10

    @classmethod
    def tile_numbers(cls, udim_tiles: tuple[tuple[int, int], ...]) -> set[int]:
        return set([cls.tile_number(*t) for t in udim_tiles])
