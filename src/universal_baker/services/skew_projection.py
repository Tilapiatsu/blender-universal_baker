from __future__ import annotations

from mathutils import Vector

from .cage_projection import CageProjection


from mathutils import Vector


class SkewProjectionService:
    @staticmethod
    def interpolate(
        projection,
        amount: float,
    ) -> Vector:

        amount = max(0.0, min(1.0, amount))

        direction = projection.normal_direction.lerp(
            projection.cage_direction,
            amount,
        )

        if direction.length_squared <= 1e-12:
            raise ValueError(
                "Skew projection produced a zero-length "
                "direction. "
                f"amount={amount}, "
                f"normal={projection.normal_direction}, "
                f"cage={projection.cage_direction}"
            )

        return direction.normalized()
