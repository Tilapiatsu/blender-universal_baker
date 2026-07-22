from __future__ import annotations

from ..properties.baker import UBK_Baker
from .collection import PropertyCollectionService
from .target_object import TargetObjectService


class BakerService(PropertyCollectionService[UBK_Baker]):
    @classmethod
    def collection(cls, owner):
        obj = TargetObjectService.active(owner)

        return obj.bakers if obj else []

    @classmethod
    def get_active_index(cls, owner):
        obj = TargetObjectService.active(owner)

        return obj.active_baker_index if obj else 0

    @classmethod
    def set_active_index(cls, owner, index):
        obj = TargetObjectService.active(owner)

        if obj:
            obj.active_baker_index = index
