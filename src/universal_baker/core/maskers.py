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

        for tile in mask.keys():
            if tile not in src_tiles:
                continue

            result_buffer = image.buffer(tile)
            mask_buffer = mask[tile]

            LOG.info(f"Masking tile : {result_buffer.name} with {mask_buffer.name}_{tile}")

            result_buffer = image.buffer(tile)

            compositor.composite(result_buffer, mask_buffer)

            image.set_buffer(tile, result_buffer)

        return image
