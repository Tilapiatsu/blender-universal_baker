from __future__ import annotations

from dataclasses import dataclass, field

import bpy
import numpy as np


@dataclass(slots=True)
class _SkewTile:
    width: int
    height: int
    values: np.ndarray


@dataclass(slots=True)
class SkewField:
    """Cached skew intensity field backed by an image or CORNER attribute."""

    tiles: dict[int, _SkewTile] = field(default_factory=dict)
    missing_value: float = 0.0

    # When present, values are in mesh-loop order rather than UV space.
    corner_values: np.ndarray | None = None

    @classmethod
    def from_attribute(
        cls,
        mesh: bpy.types.Mesh,
        attribute_name: str,
        *,
        missing_value: float = 0.0,
    ) -> SkewField:
        """
        Create a skew field from a scalar FLOAT attribute on the CORNER domain.

        Values are stored in mesh loop order. The mesh passed here must have
        the same loop ordering as the mesh used later by SkewCageBuilder.
        """

        attribute = mesh.attributes.get(attribute_name)

        if attribute is None:
            raise ValueError(f"Mesh {mesh.name!r} has no attribute {attribute_name!r}.")

        if attribute.domain != "CORNER":
            raise ValueError(f"Attribute {attribute_name!r} must use the CORNER domain; got {attribute.domain!r}.")

        if attribute.data_type != "FLOAT":
            raise ValueError(f"Attribute {attribute_name!r} must be a FLOAT attribute; got {attribute.data_type!r}.")

        if len(attribute.data) != len(mesh.loops):
            raise ValueError(
                f"Attribute {attribute_name!r} has {len(attribute.data)} "
                f"values, but mesh {mesh.name!r} has "
                f"{len(mesh.loops)} loops."
            )

        values = np.empty(
            len(attribute.data),
            dtype=np.float32,
        )

        attribute.data.foreach_get("value", values)

        # Keep the field independent of subsequent mesh attribute edits.
        values = np.clip(values, 0.0, 1.0)

        return cls(
            missing_value=float(missing_value),
            corner_values=values,
        )

    @classmethod
    def from_image(
        cls,
        image: bpy.types.Image,
        channel: int = 0,
        missing_value: float = 0.0,
    ) -> SkewField:
        """
        Keep your existing image/UDIM implementation here unchanged.

        It should return a SkewField whose `tiles` dictionary contains the
        cached image tiles and whose `corner_values` is None.
        """
        # Insert the existing from_image() implementation here.
        raise NotImplementedError("Keep the existing image/UDIM from_image() implementation.")

    def sample(self, uvs: np.ndarray) -> np.ndarray:
        """
        Sample intensities using the same interface for both source types.

        Image-backed fields sample UV coordinates.
        Attribute-backed fields return values in mesh-loop order; in this
        case, `uvs` is used to validate the expected number of corners.
        """

        uvs = np.asarray(uvs, dtype=np.float32)

        if uvs.ndim != 2 or uvs.shape[1] != 2:
            raise ValueError("uvs must have shape (N, 2)")

        # CORNER attributes are already sampled: each value belongs to one
        # loop. Do not sample by UV, because distinct corners may share the
        # same UV coordinate while carrying different skew intensities.
        if self.corner_values is not None:
            if len(uvs) != len(self.corner_values):
                raise ValueError(
                    "The number of UV coordinates does not match the "
                    "number of cached corner attribute values. Make sure "
                    "the attribute and UVs come from the same mesh topology "
                    "and loop ordering."
                )

            return self.corner_values.copy()

        # Image-backed path: keep the existing tile-aware sampling logic.
        return self._sample_image_uvs(uvs)

    def _sample_image_uvs(self, uvs: np.ndarray) -> np.ndarray:
        """
        Move the existing tile-aware sample() implementation here,
        unchanged, so it samples self.tiles.
        """
        raise NotImplementedError("Move the existing UDIM image sampling body into this method.")
