from __future__ import annotations


from ..constant import LOG
from ..compositors.base import Compositor
from ..runtime.image_handle import ImageHandle


class ImageAccumulator:
    def __init__(self, image_handle: ImageHandle):
        self._result = image_handle

    def accumulate(self, image: ImageHandle, compositor: Compositor) -> None:
        """Accumulate Image to buffer"""
        LOG.info(f"Accumulate image : {image.artifact.name}")
        LOG.info(f"{len(image.tiles())} tile(s) found")
        src_tiles = image.tiles()
        dst_tiles = self._result.tiles()

        for tile in src_tiles:
            LOG.info(f"Accumulate tile : {tile}")

            if tile not in dst_tiles:
                self._result.set_empty_buffer(tile)

            compositor.composite(self._result.buffer(tile), image.buffer(tile))

    def result(self) -> ImageHandle:
        """Returns Accumulated buffer"""
        return self._result
