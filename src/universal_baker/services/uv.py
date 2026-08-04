from __future__ import annotations

import math


class UVService:
    @staticmethod
    def detect_udim_tiles(obj, uv_name) -> tuple:
        tiles = set()

        mesh = obj.data

        if mesh is None:
            return tuple(tiles)

        uv_layer = obj.data.uv_layers[uv_name]

        if uv_layer is None:
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
