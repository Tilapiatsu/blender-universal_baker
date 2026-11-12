from __future__ import annotations

import bpy
from mathutils import Vector


class BoundingBoxService:
    @staticmethod
    def get_world_aabb(obj_list: list[bpy.types.object]):
        """
        Takes a list of Blender objects and returns the min and max
        world-space vectors of their combined Axis-Aligned Bounding Box.

        Args:
            obj_list (list): A list of bpy.types.Object instances.

        Returns:
            tuple: (min_vector, max_vector) as mathutils.Vector objects,
                or (None, None) if the list is empty or invalid.
        """
        if not obj_list:
            return None, None

        min_x = min_y = min_z = float("inf")
        max_x = max_y = max_z = float("-inf")

        valid_obj_count = 0

        for obj in obj_list:
            if obj.type != "MESH":
                continue

            # Check if the object has a bounding box (e.g., meshes, curves)
            if not hasattr(obj, "bound_box") or not obj.bound_box:
                continue

            valid_obj_count += 1

            # obj.bound_box provides 8 corners in local space
            for corner in obj.bound_box:
                # Transform the local corner to world space using matrix_world
                world_corner = obj.matrix_world @ Vector(corner)

                min_x = min(min_x, world_corner.x)
                min_y = min(min_y, world_corner.y)
                min_z = min(min_z, world_corner.z)

                max_x = max(max_x, world_corner.x)
                max_y = max(max_y, world_corner.y)
                max_z = max(max_z, world_corner.z)

        if valid_obj_count == 0 or min_x == float("inf") or max_x == float("-inf"):
            return None, None

        return Vector((min_x, min_y, min_z)), Vector((max_x, max_y, max_z))
