from __future__ import annotations

from ..properties.object import UBK_TargetObject
from .collection import PropertyCollectionService


class TargetObjectService(PropertyCollectionService[UBK_TargetObject]):
    @classmethod
    def collection(cls, owner):
        return owner.target_objects

    @classmethod
    def get_active_index(cls, owner):
        return owner.active_target_object_index

    @classmethod
    def set_active_index(cls, owner, index):
        owner.active_target_object_index = index
