from __future__ import annotations

from dataclasses import dataclass

import bpy
from mathutils import Matrix, Vector

from .uv_mesh import UvMesh
from .uv_rasterizer import (
    INVALID_TRIANGLE,
    UvRasterization,
)


@dataclass(slots=True)
class BakeSurfaceSample:
    """
    A single point sampled from the target surface.

    All spatial data is expressed in world space.

    The barycentric coordinates are retained because they are useful later
    when reconstructing additional per-vertex attributes.
    """

    triangle_index: int

    barycentric: tuple[float, float, float]

    position: Vector
    normal: Vector

    uv: Vector


class UvSurfaceSampler:
    """
    Resolves UV rasterization samples against a Blender mesh.

    The rasterizer determines:

        pixel -> UV triangle + barycentric coordinates

    This sampler determines:

        triangle + barycentric coordinates
            -> world-space position + normal
    """

    def __init__(
        self,
        mesh: bpy.types.Mesh,
        uv_mesh: UvMesh,
        matrix_world: Matrix,
    ) -> None:
        self._mesh = mesh
        self._uv_mesh = uv_mesh
        self._matrix_world = matrix_world.copy()

        self._normal_matrix = matrix_world.to_3x3().inverted().transposed()

    def sample(
        self,
        rasterization: UvRasterization,
        x: int,
        y: int,
    ) -> BakeSurfaceSample | None:
        """
        Resolve one output pixel into a world-space surface sample.

        Returns None when the pixel isn't covered by a UV triangle.
        """

        triangle_index = rasterization.triangle_index_at(x, y)

        if triangle_index == INVALID_TRIANGLE:
            return None

        barycentric = rasterization.barycentric_at(x, y)
        uv = rasterization.uv_at(x, y)

        return self.sample_triangle(
            triangle_index=triangle_index,
            barycentric=barycentric,
            uv=uv,
        )

    def sample_triangle(
        self,
        triangle_index: int,
        barycentric: tuple[float, float, float],
        uv: tuple[float, float],
    ) -> BakeSurfaceSample:
        """
        Resolve a triangle and barycentric coordinates into a surface sample.
        """

        if not 0 <= triangle_index < len(self._uv_mesh.triangles):
            raise IndexError(f"Triangle index {triangle_index} is outside the UV mesh.")

        triangle = self._uv_mesh.triangles[triangle_index]

        w0, w1, w2 = barycentric

        vertex0 = self._mesh.vertices[triangle.vertex_indices[0]]
        vertex1 = self._mesh.vertices[triangle.vertex_indices[1]]
        vertex2 = self._mesh.vertices[triangle.vertex_indices[2]]

        position_local = vertex0.co * w0 + vertex1.co * w1 + vertex2.co * w2

        position_world = self._matrix_world @ position_local

        normal_local = vertex0.normal * w0 + vertex1.normal * w1 + vertex2.normal * w2

        if normal_local.length_squared > 0.0:
            normal_local.normalize()

        normal_world = self._normal_matrix @ normal_local

        if normal_world.length_squared > 0.0:
            normal_world.normalize()

        return BakeSurfaceSample(
            triangle_index=triangle_index,
            barycentric=barycentric,
            position=position_world,
            normal=normal_world,
            uv=Vector(uv),
        )

    def iter_samples(
        self,
        rasterization: UvRasterization,
    ):
        """
        Iterate over every covered pixel.

        Yields:

            (x, y, BakeSurfaceSample)

        Pixels outside the UV islands are skipped.
        """

        width = rasterization.width
        height = rasterization.height

        for y in range(height):
            for x in range(width):
                sample = self.sample(
                    rasterization,
                    x,
                    y,
                )

                if sample is not None:
                    yield x, y, sample
