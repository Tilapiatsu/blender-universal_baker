from __future__ import annotations

from dataclasses import dataclass

import bpy
from mathutils import Matrix, Vector

from .uv_mesh import UvMesh
from .uv_rasterizer import UvRasterization
from .uv_surface import BakeSurfaceSample


@dataclass(slots=True)
class CageProjection:
    """
    A projection ray generated from a target surface sample and its
    corresponding cage surface position.

    All spatial values are expressed in world space.
    """

    origin: Vector
    direction: Vector
    cage_distance: float


class CageProjectionService:
    """
    Builds projection rays from target surface samples and corresponding
    cage surface samples.

    The service intentionally contains no skew-correction logic.

    Its only responsibility is to answer:

        "Given this target surface position and the corresponding cage
         surface position, what is the cage projection ray?"
    """

    def create_projection(
        self,
        surface_sample: BakeSurfaceSample,
        cage_position: Vector,
    ) -> CageProjection:
        """
        Create a cage projection from two corresponding surface positions.

        The ray starts at the target surface and points toward the cage.

        The distance between the surfaces is used as the default maximum
        projection distance.
        """

        offset = cage_position - surface_sample.position
        distance = offset.length

        if distance <= 1e-12:
            raise ValueError("Cannot create a cage projection when target and cage positions are coincident.")

        direction = offset / distance

        return CageProjection(
            origin=surface_sample.position.copy(),
            direction=direction,
            cage_distance=distance,
        )


class CageSurfaceSampler:
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

        if triangle_index < 0:
            return None

        barycentric = rasterization.barycentric_at(x, y)

        triangle = self._uv_mesh.triangles[triangle_index]

        w0, w1, w2 = barycentric

        vertex0 = self._mesh.vertices[triangle.vertex_indices[0]]
        vertex1 = self._mesh.vertices[triangle.vertex_indices[1]]
        vertex2 = self._mesh.vertices[triangle.vertex_indices[2]]

        position_local = vertex0.co * w0 + vertex1.co * w1 + vertex2.co * w2

        return self._matrix_world @ position_local
