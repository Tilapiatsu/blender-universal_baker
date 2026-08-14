from __future__ import annotations

import numpy as np


from ..resources.image_buffer import ImageBuffer
from ..resources.label_buffer import LabelBuffer
from .tile_set import TileSet
from .image_mask import ImageMask
from .label_set import LabelSet


# TODO: need to test in depth to make sure it works fine
class UvOwnershipMask:
    """
    Runtime Voronoi ownership information.

    Each pixel is assigned to the closest target object UV surface.
    """

    def __init__(
        self,
        labels: LabelSet,
        resolution: tuple[int, int],
        object_uuids: dict[int, str],
        name: str = "UV Ownership",
    ):
        self.labels = labels
        self.resolution = resolution
        self.object_uuids = object_uuids
        self.name = name

    def get_tile(self, tile: int) -> LabelBuffer | None:
        return self.labels[tile]

    def mask_for_object(self, object_uuid: str) -> ImageMask:
        """Create a binary ImageMask for one object."""

        label = None

        for object_label, name in self.object_uuids.items():
            if name == object_uuid:
                label = object_label
                break

        if label is None:
            raise KeyError(f"Unknown ownership object: {object_uuid!r}")

        tiles = TileSet()

        for tile, ownership in self.labels.tile_buffers:
            height, width = ownership.shape

            buffer = ImageBuffer.empty(width, height, name=f"{self.name}_{object_uuid}_{tile}")

            pixels = buffer.pixels.reshape(height, width, 4)

            pixels[..., 3] = (ownership == label).astype(np.float32)

            tiles[tile] = buffer

        return ImageMask(
            tiles,
            name=f"{self.name}_{object_uuid}",
        )
