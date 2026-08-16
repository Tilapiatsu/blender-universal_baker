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


@dataclass(slots=True)
class OwnershipDatas:
    _index_uuids: dict[int, OwnershipData] = field(default_factory=dict)
    _last_index: int = 0

    def add(self, name: str, uuid: str, uv_layer: str) -> None:
        self._last_index += 1
        od = OwnershipData(
            object_name=name,
            object_uuid=uuid,
            uv_layer=uv_layer,
        )
        self._index_uuids[self._last_index] = od

    def last_item_index(self) -> int:
        return self._last_index

    def keys(self):
        return list(self._index_uuids.keys())

    def values(self):
        return self._index_uuids.values()

    def update(self, *args, **kwargs):
        return self._index_uuids.update(*args, **kwargs)

    def items(self):
        return self._index_uuids.items()

    def __contains__(self, key: int) -> bool:
        return key in self._index_uuids

    def __getitem__(self, key: int) -> OwnershipData:
        return self._index_uuids[key]

    def __repr__(self) -> str:
        return repr(self._index_uuids)

    def __len__(self) -> int:
        return len(self._index_uuids)

    def __delitem__(self, key: int) -> None:
        del self._index_uuids[key]
