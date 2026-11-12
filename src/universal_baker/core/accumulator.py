from __future__ import annotations

from ..compositors.base import Compositor
from ..constant import LOG
from ..runtime.image_handle import ImageHandle
from ..runtime.tile_set import TileSet


class ImageAccumulator:
    def __init__(self, tile_set: TileSet):
        self._result = tile_set

    def accumulate(self, image: ImageHandle, compositor: Compositor) -> None:
        """Accumulate Image to buffer"""
        LOG.info(f"Accumulate image : {image.artifact.name}")
        LOG.info(f"{len(image.tiles())} tile(s) found")
        src_tiles = image.tiles()
        dst_tiles = self._result.tiles

        for tile in src_tiles:
            LOG.info(f"Accumulate tile : {tile}")

            if tile not in dst_tiles:
                buffer = image.buffer(tile)
                self._result.add_empty_tile(tile, (buffer.height, buffer.width), True)

            result_buffer = self._result[tile]

            compositor.composite(result_buffer, image.buffer(tile))

            self._result[tile] = result_buffer

    def result(self) -> TileSet:
        """Returns Accumulated Tileset"""
        return self._result
