from __future__ import annotations

import numpy as np

from ..constant import LOG
from ..resources.image_buffer import ImageBuffer
from ..resources.label_buffer import LabelBuffer
from .label_set import LabelSet
from .tile_set import TileSet


class UvOwnershipMask:
    """
    Runtime Voronoi ownership information.

    Each pixel is assigned to the closest target object UV surface.
    """

    def __init__(
        self,
        labels: LabelSet,
        resolution: tuple[int, int],
        object_index_uuids: dict[int, str],
        name: str = "UV Ownership",
    ):
        self.labels = labels
        self.resolution = resolution
        self.object_index_uuids = object_index_uuids
        self.name = name

    def set(self, uv_ownership_mask: UvOwnershipMask) -> None:
        self.labels = uv_ownership_mask.labels
        self.resolution = uv_ownership_mask.resolution
        self.object_index_uuids = uv_ownership_mask.object_index_uuids
        self.name = uv_ownership_mask.name

    def get_tile(self, tile: int) -> LabelBuffer | None:
        return self.labels[tile]

    def mask_for_object(self, object_uuid: str) -> TileSet:
        """Create a binary ImageMask for one object."""

        label = None

        for object_index, uuid in self.object_index_uuids.items():
            if uuid == object_uuid:
                label = object_index
                break

        if label is None:
            raise KeyError(f"Unknown ownership object: {object_uuid!r}")

        tiles = TileSet()

        for tile, ownership in self.labels.tile_buffers:
            LOG.debug(f"Writing tile {tile} for object {label}")
            height, width = ownership.shape

            buffer = ImageBuffer.empty(width, height, name=self.name)

            pixels = buffer.pixels.reshape(height, width, 4)

            pixels[..., 3] = (ownership.pixels == label).astype(np.float32)

            tiles[tile] = buffer

        return tiles
        # return ImageMask(
        #     tiles,
        #     name=f"{self.name}_{object_uuid}",
        # )
