from __future__ import annotations

from dataclasses import dataclass

import bpy
import numpy as np


@dataclass(slots=True)
class SkewField:
    """Cached scalar intensity field sampled in UV space."""

    width: int
    height: int
    values: np.ndarray  # Shape: (height, width), float32

    @classmethod
    def from_image(
        cls,
        image: bpy.types.Image,
        channel: int = 0,
    ) -> SkewField:
        width, height = image.size

        if width <= 0 or height <= 0:
            raise ValueError(f"Skew image {image.name!r} has invalid dimensions.")

        channels = 4
        pixels = np.empty(
            width * height * channels,
            dtype=np.float32,
        )

        image.pixels.foreach_get(pixels)

        rgba = pixels.reshape(height, width, channels)

        if not 0 <= channel < channels:
            raise ValueError(f"Invalid image channel: {channel}")

        values = rgba[:, :, channel].copy()

        return cls(
            width=width,
            height=height,
            values=values,
        )

    def sample(self, uvs: np.ndarray) -> np.ndarray:
        """
        Bilinearly sample intensity at UV coordinates.

        Args:
            uvs: Array of shape (N, 2), with U and V coordinates.

        Returns:
            Float32 array of shape (N,), clamped to [0, 1].

        UVs outside the image are clamped to the image border.
        """

        uvs = np.asarray(uvs, dtype=np.float32)

        if uvs.ndim != 2 or uvs.shape[1] != 2:
            raise ValueError("uvs must have shape (N, 2)")

        # Map UV coordinates to pixel-center coordinates.
        x = np.clip(
            uvs[:, 0] * self.width - 0.5,
            0.0,
            self.width - 1.0,
        )
        y = np.clip(
            uvs[:, 1] * self.height - 0.5,
            0.0,
            self.height - 1.0,
        )

        x0 = np.floor(x).astype(np.intp)
        y0 = np.floor(y).astype(np.intp)

        x1 = np.minimum(x0 + 1, self.width - 1)
        y1 = np.minimum(y0 + 1, self.height - 1)

        tx = x - x0
        ty = y - y0

        # NumPy indexes [row, column] = [y, x].
        v00 = self.values[y0, x0]
        v10 = self.values[y0, x1]
        v01 = self.values[y1, x0]
        v11 = self.values[y1, x1]

        top = v00 * (1.0 - tx) + v10 * tx
        bottom = v01 * (1.0 - tx) + v11 * tx

        result = top * (1.0 - ty) + bottom * ty

        return np.clip(result, 0.0, 1.0)
