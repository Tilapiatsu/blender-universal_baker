from __future__ import annotations

from ..properties.baker import UBK_Baker
from .collection import PropertyCollectionService
from .object import ObjectService


class MapService(PropertyCollectionService[UBK_Baker]):
    @classmethod
    def collection(cls, owner):
        obj = ObjectService.active(owner)

        return obj.maps if obj else []

    @classmethod
    def get_active_index(cls, owner):
        obj = ObjectService.active(owner)

        return obj.active_baker_index if obj else 0

    @classmethod
    def set_active_index(cls, owner, index):
        obj = ObjectService.active(owner)

        if obj:
            obj.active_baker_index = index
