from __future__ import annotations

from dataclasses import dataclass

import bpy


@dataclass(slots=True, frozen=True)
class OwnershipData:
    object_name: str
    layer_name: str

    @property
    def blender_object(self) -> bpy.types.Object | None:
        return bpy.data.objects.get(self.object_name)
