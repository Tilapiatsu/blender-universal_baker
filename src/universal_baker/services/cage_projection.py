from __future__ import annotations

from dataclasses import dataclass

from mathutils import Vector

from .uv_surface import BakeSurfaceSample


@dataclass(slots=True)
class CageProjection:
    """
    Geometric information required to construct a custom bake ray.

    All spatial values are expressed in world space.
    """

    origin: Vector
    normal_direction: Vector
    cage_direction: Vector
    cage_distance: float


class CageProjectionService:
    def create_projection(
        self,
        surface_sample: BakeSurfaceSample,
        cage_position: Vector,
    ) -> CageProjection:

        origin = surface_sample.position.copy()

        normal_direction = surface_sample.normal.copy()

        if normal_direction.length_squared <= 1e-12:
            raise ValueError("Target surface has an invalid normal.")

        normal_direction.normalize()

        cage_offset = origin - cage_position
        cage_distance = cage_offset.length

        if cage_distance <= 1e-12:
            raise ValueError(
                f"Target and cage positions are coincident.\ndistance={cage_distance}, origin={origin}, cage_position={cage_position}"
            )

        cage_direction = cage_offset / cage_distance

        return CageProjection(
            origin=origin,
            normal_direction=normal_direction,
            cage_direction=cage_direction,
            cage_distance=cage_distance,
        )
