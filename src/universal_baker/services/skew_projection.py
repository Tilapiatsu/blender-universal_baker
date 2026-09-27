from __future__ import annotations

from mathutils import Vector

from .cage_projection import CageProjection


class SkewProjectionService:
    def interpolate(
        self,
        projection: CageProjection,
        amount: float,
    ) -> Vector:

        amount = max(0.0, min(1.0, amount))

        direction = projection.normal_direction.lerp(
            projection.cage_direction,
            amount,
        )

        if direction.length_squared <= 1e-12:
            raise ValueError("Skew interpolation produced an invalid direction.")

        return direction.normalized()
