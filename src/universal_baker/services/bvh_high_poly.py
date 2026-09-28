from __future__ import annotations

from dataclasses import dataclass

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


@dataclass(slots=True)
class BVHRayHit:
    position: Vector
    normal: Vector
    distance: float
    polygon_index: int


class HighPolyBVHService:
    """
    BVH representation of an evaluated high-poly bake source.

    The public ray-cast API operates in world space.
    """

    def __init__(self) -> None:
        self._bvh: BVHTree | None = None

        self._world_matrix: Matrix | None = None
        self._inverse_world_matrix: Matrix | None = None
        self._normal_matrix: Matrix | None = None

    def build(
        self,
        obj: bpy.types.Object,
        depsgraph: bpy.types.Depsgraph,
    ) -> None:
        """
        Build the BVH from the evaluated object.

        The BVH itself is built in object-local space.
        """
        self.clear()

        if obj is None:
            raise ValueError("Cannot build BVH from None")

        if obj.type != "MESH":
            raise TypeError(f"BVH source must be a MESH object, got {obj.type!r}")

        self._bvh = BVHTree.FromObject(
            obj,
            bpy.context.evaluated_depsgraph_get(),
            deform=True,
            cage=False,
        )

        if self._bvh is None:
            raise RuntimeError(f"BVHTree.FromObject() returned None for {obj.name!r}")

        self._world_matrix = obj.matrix_world.copy()
        self._inverse_world_matrix = self._world_matrix.inverted()

        self._normal_matrix = self._world_matrix.to_3x3().inverted().transposed()

    def clear(self) -> None:
        self._bvh = None
        self._world_matrix = None
        self._inverse_world_matrix = None
        self._normal_matrix = None

    def ray_cast(
        self,
        origin: Vector,
        direction: Vector,
        max_distance: float,
    ) -> BVHRayHit | None:
        """
        Cast a world-space ray against the high-poly BVH.

        Parameters
        ----------
        origin:
            Ray origin in world space.

        direction:
            Ray direction in world space.

        max_distance:
            Maximum ray distance in world-space units.
        """

        if self._bvh is None:
            raise RuntimeError("High-poly BVH has not been built.")

        if self._inverse_world_matrix is None or self._world_matrix is None or self._normal_matrix is None:
            raise RuntimeError("High-poly BVH transform data is not initialized.")

        if direction.length_squared <= 1e-12:
            raise ValueError("Cannot cast a ray with a zero-length direction.")

        direction = direction.normalized()

        # ------------------------------------------------------------------
        # Transform the ray into the BVH's local coordinate system.
        # ------------------------------------------------------------------

        origin_local = self._inverse_world_matrix @ origin

        direction_local = self._inverse_world_matrix.to_3x3() @ direction

        local_direction_length = direction_local.length

        if max_distance < 0.0:
            raise ValueError("Maximum ray distance cannot be negative.")
        if max_distance == 0.0:
            local_max_distance = float("inf")
        else:
            local_max_distance = max_distance * local_direction_length

        if local_direction_length <= 1e-12:
            return None

        direction_local.normalize()

        # A normalized local direction means the BVH distance is measured
        # in local units. Convert the world-space maximum distance using
        # the scale of the transformed direction.
        local_max_distance = max_distance * local_direction_length

        # ------------------------------------------------------------------
        # Perform the actual BVH query.
        # ------------------------------------------------------------------

        (
            location_local,
            normal_local,
            polygon_index,
            distance_local,
        ) = self._bvh.ray_cast(
            origin_local,
            direction_local,
            local_max_distance,
        )

        if location_local is None:
            return None

        # ------------------------------------------------------------------
        # Convert the result back into world space.
        # ------------------------------------------------------------------

        position_world = self._world_matrix @ location_local

        normal_world = self._normal_matrix @ normal_local

        if normal_world.length_squared > 1e-12:
            normal_world.normalize()

        distance_world = (position_world - origin).length

        return BVHRayHit(
            position=position_world,
            normal=normal_world,
            distance=distance_world,
            polygon_index=polygon_index,
        )
