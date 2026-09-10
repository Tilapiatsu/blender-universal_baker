from __future__ import annotations

import bpy

from ..properties.object import UBK_TargetObject

LOG_SCOPE = "Cage Object"


class CageObjectService:
    """Service to create and manage generated cage objects"""

    CAGE_SUFFIX = "UBK_CAGE"
    MODIFIER_NAME = "UBK_DISPLACE"
    MODIFIER_TYPE = "DISPLACE"
    VERTEX_GROUP_NAME = "UBK_DISPLACE"

    @classmethod
    def acquire(cls, target: UBK_TargetObject) -> bpy.types.Object:
        if target.settings_cage.cage_object_generated is not None:
            return target.settings_cage.cage_object_generated

        cage = cls._get_or_create_cage(target)

        target.settings_cage.cage_object_generated = cage

        return cage

    @classmethod
    def _get_or_create_cage(cls, target: bpy.types.Object) -> bpy.types.Object:
        cage_name = cls._get_cage_name(target.name)
        cage = bpy.data.objects.get(cage_name)

        if cage is not None and cage.data == target.data:
            cls._ensure_modifiers(cage)
            return cage

        cage = target.copy()
        cage.name = cage_name

        cls._ensure_modifiers(cage)

        return cage

    @classmethod
    def _ensure_modifiers(cls, cage: bpy.types.Object) -> None:
        cls._ensure_vertex_group(cage)

        modifier = None

        for m in cage.modifiers:
            if m.type == cls.MODIFIER_TYPE and m.name == cls.MODIFIER_NAME:
                modifier = m
                break

        if modifier is None:
            modifier = cage.modifiers.new(type=cls.MODIFIER_TYPE, name=cls.MODIFIER_NAME)

        modifier.vertex_group = cage.vertex_groups.get(cls.VERTEX_GROUP_NAME)

    @classmethod
    def _ensure_vertex_group(cls, cage: bpy.types.Object) -> None:
        vertex_group = cage.vertex_group.get(cls.VERTEX_GROUP_NAME)

        if vertex_group is None:
            vertex_group = cage.vertex_group.new(name=cls.VERTEX_GROUP_NAME)

    @classmethod
    def _get_cage_name(cls, target_name: str) -> str:
        return f"{target_name}_{cls.CAGE_SUFFIX}"
