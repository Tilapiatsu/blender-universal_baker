from __future__ import annotations

from ..properties.packer import UBK_Pack
from .collection import PropertyCollectionService


class PackService(PropertyCollectionService[UBK_Pack]):
    @classmethod
    def collection(cls, owner):
        return owner.objects

    @classmethod
    def get_active_index(cls, owner):
        return owner.active_object_index

    @classmethod
    def set_active_index(cls, owner, index):
        owner.active_object_index = index
