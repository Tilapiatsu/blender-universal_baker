from __future__ import annotations

from dataclasses import dataclass, field

import bpy


@dataclass(slots=True, frozen=True)
class OwnershipData:
    object_name: str
    object_uuid: str
    uv_layer: str

    @property
    def blender_object(self) -> bpy.types.Object | None:
        return bpy.data.objects.get(self.object_name)

    @property
    def mesh(self) -> bpy.types.Mesh | None:
        obj = self.blender_object

        if obj is None or obj.type != "MESH":
            return None

        return obj.data


@dataclass(slots=True)
class OwnershipDatas:
    _objects: dict[str, OwnershipData] = field(default_factory=dict)

    def add(
        self,
        name: str,
        uuid: str,
        uv_layer: str,
    ) -> None:
        self._objects[uuid] = OwnershipData(
            object_name=name,
            object_uuid=uuid,
            uv_layer=uv_layer,
        )

    def get(self, uuid: str) -> OwnershipData | None:
        return self._objects.get(uuid)

    def keys(self):
        return self._objects.keys()

    def values(self):
        return self._objects.values()

    def items(self):
        return self._objects.items()

    def __contains__(self, uuid: str) -> bool:
        return uuid in self._objects

    def __getitem__(self, uuid: str) -> OwnershipData:
        return self._objects[uuid]

    def __len__(self) -> int:
        return len(self._objects)

    def __delitem__(self, uuid: str) -> None:
        del self._objects[uuid]

    def __repr__(self) -> str:
        return repr(self._objects)
