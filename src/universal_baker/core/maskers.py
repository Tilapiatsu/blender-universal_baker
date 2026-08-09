from __future__ import annotations


from ..constant import LOG
from ..compositors.base import Compositor
from ..runtime.image_handle import ImageHandle
from ..runtime.tile_set import TileSet


class ImageMasker:
    @staticmethod
    def apply_mask(image: ImageHandle, mask: TileSet, compositor: Compositor) -> ImageHandle:
        """Apply Mask to Image"""
        LOG.info(f"{len(mask)} tile(s) found")
        src_tiles = image.tiles()

        for tile in src_tiles:
            LOG.info(f"Masking tile : {tile}")

            if tile not in mask.keys():
                continue

            result_buffer = image.buffer(tile)

            compositor.composite(result_buffer, mask[tile].buffer)

            image.set_buffer(tile, result_buffer)

        return image
