from __future__ import annotations

from dataclasses import dataclass

import bpy

from ..constant import LOG


@dataclass(slots=True)
class CageSettings:
    cage_object_name: str | None
    mode: str = "NONE"
    cage_extrusion: float = 0.1
    max_ray_distance: float = 0.0
    extrusion_group_name: str = "UBK_EXTRUSION_GROUP"
    skew_map_name: str | None = None

    @property
    def cage_object(self) -> bpy.types.Object | None:
        if self.cage_object_name is None or self.mode == "NONE":
            return None

        cage_object = bpy.data.objects.get(self.cage_object_name)

        if cage_object is None:
            LOG.error(f"Cage Object {self.cage_object_name} not found")

        return cage_object

    @property
    def extrusion_group(self) -> bpy.types.VertexGroup | None:
        cage_object = self.cage_object

        if cage_object is None:
            return

        group = cage_object.vertex_groups.get(self.extrusion_group_name)

        return group

    @property
    def skew_map(self) -> bpy.types.Image | None:
        if self.skew_map_name is None:
            return None

        skew_map = bpy.data.images.get(self.skew_map_name)

        return skew_map
