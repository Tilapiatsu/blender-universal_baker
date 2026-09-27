from __future__ import annotations

import bpy

from mathutils import Matrix, Vector

from .uv_mesh import UvMesh
from .uv_rasterizer import INVALID_TRIANGLE, UvRasterization


class CageSurfaceSampler:
    """
    Samples the cage using the same UV triangle and barycentric coordinates
    used to sample the target.

    The first implementation assumes that target and cage have matching
    topology and corresponding UVs.
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

    def sample(
        self,
        rasterization: UvRasterization,
        x: int,
        y: int,
    ) -> Vector | None:

        triangle_index = rasterization.triangle_index_at(x, y)

        if triangle_index == INVALID_TRIANGLE:
            return None

        barycentric = rasterization.barycentric_at(x, y)

        triangle = self._uv_mesh.triangles[triangle_index]

        w0, w1, w2 = barycentric

        vertex0 = self._mesh.vertices[triangle.vertex_indices[0]]
        vertex1 = self._mesh.vertices[triangle.vertex_indices[1]]
        vertex2 = self._mesh.vertices[triangle.vertex_indices[2]]

        position_local = vertex0.co * w0 + vertex1.co * w1 + vertex2.co * w2

        return self._matrix_world @ position_local
