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
    World-space BVH ray casting against an evaluated high-poly object.
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
        evaluated_object = obj.evaluated_get(depsgraph)

        self._bvh = BVHTree.FromObject(
            evaluated_object,
            depsgraph,
        )

        if self._bvh is None:
            raise RuntimeError(f"Unable to build BVH for object '{obj.name}'.")

        self._world_matrix = evaluated_object.matrix_world.copy()
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
        if self._bvh is None:
            raise RuntimeError("BVH has not been built.")

        if self._inverse_world_matrix is None or self._normal_matrix is None:
            raise RuntimeError("BVH transform data is not initialized.")

        # Convert ray into object space.
        origin_local = self._inverse_world_matrix @ origin

        direction_local = self._inverse_world_matrix.to_3x3() @ direction

        direction_local.normalize()

        # Because direction is normalized after transforming,
        # the BVH distance is in local-space units.
        #
        # For non-uniform scaling this means max_distance must
        # be converted appropriately. We will handle that explicitly
        # once the ray convention is finalized.
        location, normal, polygon_index, distance = self._bvh.ray_cast(
            origin_local,
            direction_local,
            max_distance,
        )

        if location is None:
            return None

        # Convert hit position back to world space.
        position_world = self._world_matrix @ location

        # Convert normal using inverse transpose.
        normal_world = self._normal_matrix @ normal

        if normal_world.length_squared > 0.0:
            normal_world.normalize()

        return BVHRayHit(
            position=position_world,
            normal=normal_world,
            distance=(position_world - origin).length,
            polygon_index=polygon_index,
        )
