from __future__ import annotations

from dataclasses import dataclass

from mathutils import Vector

from .cage_projection import CageProjection


@dataclass(slots=True)
class ProjectionRay:
    origin: Vector
    direction: Vector
    max_distance: float


class ProjectionRayBuilder:
    def build(
        self,
        projection: CageProjection,
        max_distance: float,
        reverse_direction: bool = False,
    ) -> ProjectionRay:

        if max_distance < 0.0:
            raise ValueError("Projection max distance cannot be negative.")

        direction = projection.cage_direction.copy()

        if direction.length_squared <= 1e-12:
            raise ValueError("Projection produced an invalid direction.")

        direction.normalize()

        if reverse_direction:
            direction.negate()

        return ProjectionRay(
            origin=projection.cage_position.copy(),
            direction=direction,
            max_distance=max_distance,
        )
