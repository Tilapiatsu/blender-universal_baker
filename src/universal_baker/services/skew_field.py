from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import bpy
import numpy as np


@dataclass(slots=True)
class _SkewTile:
    width: int
    height: int
    values: np.ndarray


@dataclass(slots=True)
class SkewField:
    """
    Cached scalar skew field.

    Tile 1001 corresponds to UV tile (0, 0).
    Tile 1002 corresponds to UV tile (1, 0).
    Tile 1011 corresponds to UV tile (0, 1).

    Pixel arrays are stored as float32 with shape (height, width).
    """

    tiles: dict[int, _SkewTile] = field(default_factory=dict)
    missing_value: float = 0.0

    @classmethod
    def from_image(
        cls,
        image: bpy.types.Image,
        channel: int = 0,
        missing_value: float = 0.0,
    ) -> SkewField:
        if not 0 <= channel < 4:
            raise ValueError(f"Invalid image channel: {channel}")

        result = cls(missing_value=missing_value)

        if image.source != "TILED":
            result.tiles[1001] = cls._read_tile_pixels(
                image,
                channel,
            )
            return result

        # A tiled image's image.pixels buffer is not a reliable way to
        # independently read every tile. Load each file-backed tile as a
        # temporary ordinary image instead.
        filepath = bpy.path.abspath(image.filepath)

        if "<UDIM>" not in filepath:
            raise ValueError(
                f"Cannot resolve UDIM tile paths for {image.name!r}. "
                "Expected a file path containing <UDIM>. "
                "Generated or packed tiled images need a separate "
                "tile extraction strategy."
            )

        for tile in image.tiles:
            tile_path = filepath.replace(
                "<UDIM>",
                str(tile.number),
            )

            if not Path(tile_path).is_file():
                # A missing tile is deliberately left uncached.
                continue

            temporary_image = None

            try:
                temporary_image = bpy.data.images.load(
                    tile_path,
                    check_existing=False,
                )

                result.tiles[tile.number] = cls._read_tile_pixels(
                    temporary_image,
                    channel,
                )

            finally:
                if temporary_image is not None:
                    bpy.data.images.remove(
                        temporary_image,
                        do_unlink=True,
                    )

        if not result.tiles:
            raise ValueError(f"No readable UDIM tile files found for {image.name!r}.")

        return result

    @staticmethod
    def _read_tile_pixels(
        image: bpy.types.Image,
        channel: int,
    ) -> _SkewTile:
        width, height = image.size

        if width <= 0 or height <= 0:
            raise ValueError(f"Image {image.name!r} has invalid dimensions.")

        rgba = np.empty(
            width * height * 4,
            dtype=np.float32,
        )

        image.pixels.foreach_get(rgba)

        rgba = rgba.reshape(height, width, 4)

        return _SkewTile(
            width=width,
            height=height,
            values=rgba[:, :, channel].copy(),
        )

    def sample(self, uvs: np.ndarray) -> np.ndarray:
        """
        Bilinearly sample a batch of UV coordinates.

        Missing tiles return missing_value.
        Coordinates outside the available UDIM tile range are not clamped
        into another tile.
        """

        uvs = np.asarray(uvs, dtype=np.float32)

        if uvs.ndim != 2 or uvs.shape[1] != 2:
            raise ValueError("uvs must have shape (N, 2)")

        output = np.full(
            len(uvs),
            self.missing_value,
            dtype=np.float32,
        )

        if len(uvs) == 0:
            return output

        # Integer tile coordinates; fractional parts are tile-local UVs.
        tile_u = np.floor(uvs[:, 0]).astype(np.int64)
        tile_v = np.floor(uvs[:, 1]).astype(np.int64)

        # Standard UDIM numbering:
        # 1001 + U + 10 * V
        tile_numbers = 1001 + tile_u + 10 * tile_v

        for tile_number in np.unique(tile_numbers):
            tile = self.tiles.get(int(tile_number))

            if tile is None:
                continue

            indices = np.flatnonzero(tile_numbers == tile_number)

            local_u = uvs[indices, 0] - tile_u[indices]
            local_v = uvs[indices, 1] - tile_v[indices]

            output[indices] = self._sample_tile(
                tile,
                local_u,
                local_v,
            )

        return output

    @staticmethod
    def _sample_tile(
        tile: _SkewTile,
        u: np.ndarray,
        v: np.ndarray,
    ) -> np.ndarray:
        # Convert local UVs to pixel-center coordinates.
        x = np.clip(
            u * tile.width - 0.5,
            0.0,
            tile.width - 1.0,
        )
        y = np.clip(
            v * tile.height - 0.5,
            0.0,
            tile.height - 1.0,
        )

        x0 = np.floor(x).astype(np.intp)
        y0 = np.floor(y).astype(np.intp)

        x1 = np.minimum(x0 + 1, tile.width - 1)
        y1 = np.minimum(y0 + 1, tile.height - 1)

        tx = x - x0
        ty = y - y0

        values = tile.values

        v00 = values[y0, x0]
        v10 = values[y0, x1]
        v01 = values[y1, x0]
        v11 = values[y1, x1]

        top = v00 * (1.0 - tx) + v10 * tx
        bottom = v01 * (1.0 - tx) + v11 * tx

        return np.clip(
            top * (1.0 - ty) + bottom * ty,
            0.0,
            1.0,
        )
