from __future__ import annotations

import math
import numpy as np
import bpy

from ..runtime.label_set import LabelSet
from ..resources.image_buffer import ImageBuffer
from ..resources.ownership import OwnershipData
from ..runtime.uv_ownership_mask import UvOwnershipMask
from ..runtime.tile_set import TileSet


class UvOwnershipService:
    """Generate zero-margin UV ownership masks from a Blender mesh."""

    @classmethod
    def create_uv_ownership_mask(
        cls,
        target_objects: list[OwnershipData],
        resolution: tuple[int, int],
        name: str,
        use_udim: bool = False,
    ) -> UvOwnershipMask:

        object_masks = {}
        for o in target_objects:
            object_mask = cls.create_mask(
                obj=o.blender_object,
                resolution=resolution,
                uv_map=o.uv_layer,
                use_udim=use_udim,
                name=f"{o.object_name}_mask",
            )
            object_masks[o.object_index] = object_mask

        labels = LabelSet()

        cls._feed_labels_from_object_masks(labels=labels, object_masks=object_masks)

        # NOTE: object index need to start at 1 because index 0 means no object
        object_uuids = {i + 1: o.object_uuid for i, o in enumerate(target_objects)}

        uv_ownership_mask = UvOwnershipMask(
            labels=labels,
            resolution=resolution,
            object_index_uuids=object_uuids,
            name=name,
        )

        return uv_ownership_mask

    @classmethod
    def create_mask(
        cls,
        obj: bpy.types.Object,
        resolution: tuple[int, int],
        *,
        uv_map: str | None = None,
        use_udim: bool = False,
        name: str | None = None,
    ) -> TileSet:
        """
        Create an ImageHandle containing a binary UV coverage mask.

        Pixels covered by a UV triangle are 1.0.
        Pixels outside UV triangles are 0.0.

        When use_udim is False, only the [0, 1] UV tile is generated.

        When use_udim is True, all UDIM tiles touched by the UVs
        are generated.
        """
        if obj.type != "MESH":
            raise TypeError(f"UV mask requires a mesh object, got {obj.type!r}")

        mesh = obj.data

        if uv_map is None:
            uv_layer = mesh.uv_layers.active
        else:
            uv_layer = mesh.uv_layers.get(uv_map)

        if uv_layer is None:
            raise ValueError(f"Object {obj.name!r} has no UV map {uv_map!r}")

        width, height = resolution

        triangles = cls._extract_triangles(
            mesh,
            uv_layer,
        )

        if use_udim:
            tile_numbers = cls._detect_tiles(triangles)
        else:
            tile_numbers = [1001]

        tiles = TileSet()

        for tile_number in tile_numbers:
            tile_u, tile_v = cls._tile_coordinates(tile_number)

            buffer = ImageBuffer.empty(
                width,
                height,
                channels=1,
                name=(name or f"{obj.name}_{uv_layer}_UVOwnership_{tile_number}"),
            )

            for triangle in triangles:
                cls._rasterize_triangle(
                    buffer,
                    triangle,
                    tile_u,
                    tile_v,
                )

            tiles.add_tile(tile_number, buffer, override=True)

        return tiles

    @classmethod
    def _feed_labels_from_object_masks(cls, labels: LabelSet, object_masks: dict[int, TileSet]) -> None:
        for index, mask in object_masks.items():
            for tile, buffer in mask.tile_buffers:
                if tile not in labels.keys():
                    labels.add_empty_tile(
                        tile=tile,
                        resolution=(
                            buffer.width,
                            buffer.height,
                        ),
                        name=buffer.name,
                    )

                label_buffer = labels[tile]

                # Set the label for each pixels which alpha is 1.0 : Meaning that is is part of the object UV Shell
                label_buffer.pixels[buffer.pixels > 0.0] = index

    # ------------------------------------------------------------------
    # UV extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_triangles(
        mesh: bpy.types.Mesh,
        uv_layer: bpy.types.MeshUVLoopLayer,
    ) -> list[tuple[tuple[float, float], tuple[float, float], tuple[float, float]]]:
        """
        Convert Blender polygons into UV triangles.

        Blender stores UVs per loop/corner, so the UV coordinate is
        retrieved through polygon.loop_indices rather than through
        mesh.vertices.
        """
        triangles = []

        for polygon in mesh.polygons:
            loop_indices = polygon.loop_indices

            if len(loop_indices) < 3:
                continue

            # Blender polygons are normally convex, but using a fan
            # triangulation keeps the implementation deterministic.
            first = uv_layer.data[loop_indices[0]].uv

            for i in range(1, len(loop_indices) - 1):
                uv1 = first
                uv2 = uv_layer.data[loop_indices[i]].uv
                uv3 = uv_layer.data[loop_indices[i + 1]].uv

                triangles.append(
                    (
                        (float(uv1.x), float(uv1.y)),
                        (float(uv2.x), float(uv2.y)),
                        (float(uv3.x), float(uv3.y)),
                    )
                )

        return triangles

    # ------------------------------------------------------------------
    # UDIM detection
    # ------------------------------------------------------------------

    @classmethod
    def _detect_tiles(
        cls,
        triangles: list[tuple[tuple[float, float], ...]],
    ) -> list[int]:
        """
        Detect UDIM tiles touched by the UV triangles.

        This first implementation checks the bounding box of each
        triangle against the integer UV grid.
        """
        tiles: set[int] = set()

        for triangle in triangles:
            min_u = min(uv[0] for uv in triangle)
            max_u = max(uv[0] for uv in triangle)

            min_v = min(uv[1] for uv in triangle)
            max_v = max(uv[1] for uv in triangle)

            min_tile_u = math.floor(min_u)
            max_tile_u = math.floor(max_u)

            min_tile_v = math.floor(min_v)
            max_tile_v = math.floor(max_v)

            for tile_v in range(min_tile_v, max_tile_v + 1):
                for tile_u in range(min_tile_u, max_tile_u + 1):
                    # Blender UDIM numbering:
                    # 1001 + U + V * 10
                    tile = 1001 + tile_u + tile_v * 10

                    if tile >= 1001:
                        tiles.add(tile)

        return sorted(tiles)

    @staticmethod
    def _tile_coordinates(tile_number: int) -> tuple[int, int]:
        """Convert a UDIM number to its U/V tile coordinates."""
        index = tile_number - 1001

        tile_v = index // 10
        tile_u = index % 10

        return tile_u, tile_v

    # ------------------------------------------------------------------
    # Rasterization
    # ------------------------------------------------------------------

    @classmethod
    def _rasterize_triangle(
        cls,
        buffer: ImageBuffer,
        triangle: tuple[
            tuple[float, float],
            tuple[float, float],
            tuple[float, float],
        ],
        tile_u: int,
        tile_v: int,
    ) -> None:
        """
        Rasterize one UV triangle into an RGBA ImageBuffer.

        The triangle is converted from UV space into pixel space.
        The mask writes:

            0 -> No triangles
            1 -> On a triangle
        for covered pixels.
        """

        (u0, v0), (u1, v1), (u2, v2) = triangle

        # Convert global UVs to coordinates local to this tile.
        u0 -= tile_u
        u1 -= tile_u
        u2 -= tile_u

        v0 -= tile_v
        v1 -= tile_v
        v2 -= tile_v

        width = buffer.width
        height = buffer.height

        # Triangle → pixel coordinates.
        x0 = u0 * width
        x1 = u1 * width
        x2 = u2 * width

        y0 = v0 * height
        y1 = v1 * height
        y2 = v2 * height

        min_x = max(
            0,
            int(math.floor(min(x0, x1, x2))),
        )

        max_x = min(
            width - 1,
            int(math.ceil(max(x0, x1, x2))),
        )

        min_y = max(
            0,
            int(math.floor(min(y0, y1, y2))),
        )

        max_y = min(
            height - 1,
            int(math.ceil(max(y0, y1, y2))),
        )

        if min_x > max_x or min_y > max_y:
            return

        area = cls._edge(
            x0,
            y0,
            x1,
            y1,
            x2,
            y2,
        )

        # Degenerate triangle.
        if abs(area) < 1e-8:
            return

        pixels = buffer.flat_pixels

        for py in range(min_y, max_y + 1):
            # Pixel center.
            y = py + 0.5

            for px in range(min_x, max_x + 1):
                x = px + 0.5

                w0 = cls._edge(
                    x1,
                    y1,
                    x2,
                    y2,
                    x,
                    y,
                )

                w1 = cls._edge(
                    x2,
                    y2,
                    x0,
                    y0,
                    x,
                    y,
                )

                w2 = cls._edge(
                    x0,
                    y0,
                    x1,
                    y1,
                    x,
                    y,
                )

                # Works regardless of triangle winding.
                if (w0 >= 0 and w1 >= 0 and w2 >= 0) or (w0 <= 0 and w1 <= 0 and w2 <= 0):
                    # index = (py * width + px) * 4
                    index = py * width + px

                    pixels[index] = 1.0
                    # pixels[index + 1] = 1.0
                    # pixels[index + 2] = 1.0
                    # pixels[index + 3] = 1.0

    @staticmethod
    def _edge(
        ax: float,
        ay: float,
        bx: float,
        by: float,
        px: float,
        py: float,
    ) -> float:
        """Signed 2D edge function."""
        return (px - ax) * (by - ay) - (py - ay) * (bx - ax)
