from __future__ import annotations

from ..properties.object import UBK_Object
from .collection import PropertyCollectionService


class ObjectService(PropertyCollectionService[UBK_Object]):
    @classmethod
    def collection(cls, owner):
        return owner.objects

    @classmethod
    def get_active_index(cls, owner):
        return owner.active_object_index

    @classmethod
    def set_active_index(cls, owner, index):
        owner.active_object_index = index
