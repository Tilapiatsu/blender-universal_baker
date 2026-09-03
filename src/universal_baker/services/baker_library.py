from __future__ import annotations


from ..preferences import UBK_BakerPath
from .collection import PropertyCollectionService


class BakerLibraryService(PropertyCollectionService[UBK_BakerPath]):
    @classmethod
    def collection(cls, owner):
        return owner.baker_libraries

    @classmethod
    def get_active_index(cls, owner):
        return owner.active_baker_library_idx

    @classmethod
    def set_active_index(cls, owner, index):
        owner.active_baker_library_idx = index
