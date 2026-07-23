from __future__ import annotations

from ..properties.packer import UBK_Packer
from .collection import PropertyCollectionService


class PackerService(PropertyCollectionService[UBK_Packer]):
    @classmethod
    def collection(cls, owner):
        return owner.packers

    @classmethod
    def get_active_index(cls, owner):
        return owner.active_packer_index

    @classmethod
    def set_active_index(cls, owner, index):
        owner.active_packer_index = index
