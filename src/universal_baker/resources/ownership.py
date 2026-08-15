from __future__ import annotations

from dataclasses import dataclass

import bpy


@dataclass(slots=True, frozen=True)
class OwnershipData:
    object_name: str
    object_uuid: str
    object_index: int
    uv_layer: str

    @property
    def blender_object(self) -> bpy.types.Object | None:
        return bpy.data.objects.get(self.object_name)


@dataclass(slots=True)
class ObjectIndexUuid:
    index: int
    uuid: str
