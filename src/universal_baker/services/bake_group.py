from __future__ import annotations

from ..properties.bake_group import UBK_BakeGroup
from .collection import PropertyCollectionService


class BakeGroupService(PropertyCollectionService[UBK_BakeGroup]):
    @classmethod
    def collection(cls, owner):
        return owner.bake_groups

    @classmethod
    def get_active_index(cls, owner):
        return owner.active_bake_group_index

    @classmethod
    def set_active_index(cls, owner, index):
        owner.active_bake_group_index = index
