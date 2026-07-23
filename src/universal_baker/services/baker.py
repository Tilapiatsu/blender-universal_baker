from __future__ import annotations


from ..properties.baker import UBK_Baker
from .collection import PropertyCollectionService
from .bake_group import BakeGroupService


class BakerService(PropertyCollectionService[UBK_Baker]):
    @classmethod
    def collection(cls, owner):
        return owner.bakers

    @classmethod
    def get_active_index(cls, owner):
        return owner.active_baker_index

    @classmethod
    def set_active_index(cls, owner, index):
        owner.active_baker_index = index
