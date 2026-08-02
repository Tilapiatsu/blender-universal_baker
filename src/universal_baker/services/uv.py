from __future__ import annotations

import math


class UVService:
    @staticmethod
    def detect_udim_tiles(obj, uv_name) -> set:
        tiles = set()

        mesh = obj.data

        if mesh is None:
            return tiles

        uv_layer = obj.data.uv_layer[uv_name]

        if uv_layer is None:
            return tiles

        for loop in mesh.loops:
            uv = uv_layer.data[loop.index].uv

            tile = (
                math.floor(uv.x),
                math.floor(uv.y),
            )

            tiles.add(tile)

        return tiles
