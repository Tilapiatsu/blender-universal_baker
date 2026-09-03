from __future__ import annotations

from ..properties.object import UBK_SourceObject
from .collection import PropertyCollectionService


class SourceObjectService(PropertyCollectionService[UBK_SourceObject]):
    @classmethod
    def collection(cls, owner):
        return owner.source_objects

    @classmethod
    def get_active_index(cls, owner):
        return owner.active_source_object_index

    @classmethod
    def set_active_index(cls, owner, index):
        owner.active_source_object_index = index
