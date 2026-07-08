from __future__ import annotations

from ..properties.object import UBK_Object
from .collection import PropertyCollectionService


class ObjectService(PropertyCollectionService[UBK_Object]):
    @classmethod
    def collection(cls, project):
        return project.objects

    @classmethod
    def get_active_index(cls, project):
        return project.active_object_index

    @classmethod
    def set_active_index(cls, project, index):
        project.active_object_index = index
