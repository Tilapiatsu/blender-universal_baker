from __future__ import annotations

from ..properties.map import UBK_Map
from .collection import PropertyCollectionService
from .object import ObjectService


class MapService(PropertyCollectionService[UBK_Map]):
    @classmethod
    def collection(cls, project):
        obj = ObjectService.active(project)

        return obj.maps if obj else []

    @classmethod
    def get_active_index(cls, project):
        obj = ObjectService.active(project)

        return obj.active_map_index if obj else 0

    @classmethod
    def set_active_index(cls, project, index):
        obj = ObjectService.active(project)

        if obj:
            obj.active_map_index = index
