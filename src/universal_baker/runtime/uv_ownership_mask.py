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
        label_to_uuid: dict[int, str] | None = None,
        name: str = "UV Ownership",
    ):
        self.labels = labels
        self.resolution = resolution
        self.label_to_uuid = label_to_uuid or {}
        self.uuid_to_label = {uuid: label for label, uuid in self.label_to_uuid.items()}
        self.name = name

    def set(self, uv_ownership_mask: UvOwnershipMask) -> None:
        self.labels = uv_ownership_mask.labels
        self.resolution = uv_ownership_mask.resolution
        self.label_to_uuid = uv_ownership_mask.label_to_uuid
        self.uuid_to_label = {uuid: label for label, uuid in self.label_to_uuid.items()}
        self.name = uv_ownership_mask.name

    def get_tile(self, tile: int) -> LabelBuffer | None:
        return self.labels[tile]

    def mask_for_object(self, object_uuid: str) -> TileSet:
        """Create a binary ImageMask for one object."""

        # ISSUE: The mask resolution should match 100% the resolution of the baker. Right now the ownership.reshape()
        # does NOT resize the array properly which could cause issue if the each baker have a different resolution:
        # Option A — generate ownership once per resolution
        # or, better:
        # Option B — ownership is resolution-independent geometry, rasterized for each bake resolution.
        # For now, Option A is much simpler.

        label = None

        uuid_to_label = {uuid: label for label, uuid in self.label_to_uuid.items()}

        try:
            label = uuid_to_label[object_uuid]
            LOG.debug(
                f"OWNERSHIP LOOKUP | uuid={object_uuid}, label={label}, known={object_uuid in self.uuid_to_label}",
            )
        except KeyError:
            raise KeyError(f"Unknown ownership object: {object_uuid!r}")

        tiles = TileSet()

        for tile, ownership in self.labels.tile_buffers:
            LOG.debug(f"Writing tile {tile} for object of label {label}")
            height, width = ownership.shape

            buffer = ImageBuffer.empty(width, height, name=self.name)

            pixels = buffer.pixels.reshape(height, width, 4)

            pixels[..., 3] = (ownership.pixels == label).astype(np.float32)

            LOG.debug(
                f"OWNERSHIP LABELS | uuid={object_uuid}, label={label}, min={pixels.min()}, max={pixels.max()},  count={np.count_nonzero(pixels == label)}"
            )
            tiles[tile] = buffer

        return tiles
