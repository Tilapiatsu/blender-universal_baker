from __future__ import annotations

from array import array
from dataclasses import dataclass

from .uv_mesh import UvMesh, UvTriangle

INVALID_TRIANGLE = -1

_EPSILON = 1e-6
_DEGENERATE_EPSILON = 1e-12


@dataclass(slots=True)
class UvRasterization:
    """
    Result of rasterizing a UvMesh into a 2D texture.

    All arrays use row-major pixel order:

        pixel_index = y * width + x

    A pixel whose triangle index is INVALID_TRIANGLE is not covered by
    any UV triangle.
    """

    width: int
    height: int

    triangle_indices: list[int]

    # Flat float arrays:
    #
    #   [w0, w1, w2, w0, w1, w2, ...]
    #
    # One barycentric triplet per pixel.
    barycentrics: array

    # Flat float array:
    #
    #   [u, v, u, v, ...]
    #
    # One UV coordinate per pixel.
    uvs: array

    def is_covered(self, x: int, y: int) -> bool:
        return self.triangle_indices[self._pixel_index(x, y)] != INVALID_TRIANGLE

    def triangle_index_at(self, x: int, y: int) -> int:
        return self.triangle_indices[self._pixel_index(x, y)]

    def barycentric_at(
        self,
        x: int,
        y: int,
    ) -> tuple[float, float, float]:
        index = self._pixel_index(x, y) * 3

        return (
            self.barycentrics[index],
            self.barycentrics[index + 1],
            self.barycentrics[index + 2],
        )

    def uv_at(
        self,
        x: int,
        y: int,
    ) -> tuple[float, float]:
        index = self._pixel_index(x, y) * 2

        return (
            self.uvs[index],
            self.uvs[index + 1],
        )

    def _pixel_index(self, x: int, y: int) -> int:
        if not 0 <= x < self.width:
            raise IndexError(f"x={x} is outside raster width {self.width}.")

        if not 0 <= y < self.height:
            raise IndexError(f"y={y} is outside raster height {self.height}.")

        return y * self.width + x


class UvRasterizer:
    """
    Rasterizes UV triangles into a texture-space representation.

    The rasterizer operates on a single UDIM tile.

    The default tile is (0, 0), corresponding to Blender's 1001 tile.

    UV coordinates are converted into tile-local coordinates:

        local_u = uv_u - tile_u
        local_v = uv_v - tile_v

    This allows the same rasterizer to later process UDIM tiles without
    changing the underlying rasterization algorithm.
    """

    def rasterize(
        self,
        mesh: UvMesh,
        width: int,
        height: int,
        *,
        tile_u: int = 0,
        tile_v: int = 0,
    ) -> UvRasterization:
        if width <= 0:
            raise ValueError(f"Raster width must be positive, got {width}.")

        if height <= 0:
            raise ValueError(f"Raster height must be positive, got {height}.")

        pixel_count = width * height

        triangle_indices = [INVALID_TRIANGLE] * pixel_count

        barycentrics = array(
            "f",
            [0.0] * (pixel_count * 3),
        )

        uvs = array(
            "f",
            [0.0] * (pixel_count * 2),
        )

        for triangle in mesh.triangles:
            self._rasterize_triangle(
                triangle=triangle,
                width=width,
                height=height,
                tile_u=tile_u,
                tile_v=tile_v,
                triangle_indices=triangle_indices,
                barycentrics=barycentrics,
                uvs=uvs,
            )

        return UvRasterization(
            width=width,
            height=height,
            triangle_indices=triangle_indices,
            barycentrics=barycentrics,
            uvs=uvs,
        )

    def _rasterize_triangle(
        self,
        triangle: UvTriangle,
        width: int,
        height: int,
        tile_u: int,
        tile_v: int,
        triangle_indices: list[int],
        barycentrics: array,
        uvs: array,
    ) -> None:
        uv0 = self._to_tile_uv(triangle.uv0, tile_u, tile_v)
        uv1 = self._to_tile_uv(triangle.uv1, tile_u, tile_v)
        uv2 = self._to_tile_uv(triangle.uv2, tile_u, tile_v)

        # Convert UV coordinates into pixel-space coordinates.
        ax = uv0[0] * width
        ay = uv0[1] * height

        bx = uv1[0] * width
        by = uv1[1] * height

        cx = uv2[0] * width
        cy = uv2[1] * height

        denominator = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)

        # Degenerate UV triangle.
        if abs(denominator) < _DEGENERATE_EPSILON:
            return

        inverse_denominator = 1.0 / denominator

        min_u = min(uv0[0], uv1[0], uv2[0])
        max_u = max(uv0[0], uv1[0], uv2[0])

        min_v = min(uv0[1], uv1[1], uv2[1])
        max_v = max(uv0[1], uv1[1], uv2[1])

        # Convert the UV bounding box to pixel coordinates.
        #
        # We deliberately allow coordinates slightly outside the tile and
        # clamp them here. This makes triangles crossing a tile boundary
        # work correctly.
        min_x = max(
            0,
            int(min_u * width),
        )

        max_x = min(
            width - 1,
            int(max_u * width),
        )

        min_y = max(
            0,
            int(min_v * height),
        )

        max_y = min(
            height - 1,
            int(max_v * height),
        )

        if min_x > max_x or min_y > max_y:
            return

        for y in range(min_y, max_y + 1):
            py = y + 0.5

            for x in range(min_x, max_x + 1):
                px = x + 0.5

                w0 = ((by - cy) * (px - cx) + (cx - bx) * (py - cy)) * inverse_denominator

                w1 = ((cy - ay) * (px - cx) + (ax - cx) * (py - cy)) * inverse_denominator

                w2 = 1.0 - w0 - w1

                if not self._is_inside(
                    w0,
                    w1,
                    w2,
                ):
                    continue

                pixel_index = y * width + x

                # First triangle wins for overlapping UVs.
                #
                # Overlapping UVs are inherently ambiguous for a bake.
                # Keeping the first deterministic result prevents later
                # triangles from silently replacing it.
                if triangle_indices[pixel_index] != INVALID_TRIANGLE:
                    continue

                triangle_indices[pixel_index] = triangle.index

                bary_index = pixel_index * 3

                barycentrics[bary_index] = w0
                barycentrics[bary_index + 1] = w1
                barycentrics[bary_index + 2] = w2

                uv_index = pixel_index * 2

                u = uv0[0] * w0 + uv1[0] * w1 + uv2[0] * w2

                v = uv0[1] * w0 + uv1[1] * w1 + uv2[1] * w2

                uvs[uv_index] = u + tile_u
                uvs[uv_index + 1] = v + tile_v

    @staticmethod
    def _to_tile_uv(
        uv: tuple[float, float],
        tile_u: int,
        tile_v: int,
    ) -> tuple[float, float]:
        return (
            uv[0] - tile_u,
            uv[1] - tile_v,
        )

    @staticmethod
    def _is_inside(
        w0: float,
        w1: float,
        w2: float,
    ) -> bool:
        return w0 >= -_EPSILON and w1 >= -_EPSILON and w2 >= -_EPSILON
