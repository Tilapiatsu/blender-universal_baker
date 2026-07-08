from __future__ import annotations
import bpy
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, PointerProperty, CollectionProperty, IntProperty
from .map import UBK_Map


class UBK_Object(PropertyGroup):
    """Bake settings for one target object."""

    enabled: BoolProperty(
        default=True,
    )

    target: PointerProperty(
        name="Target",
        type=bpy.types.Object,
    )

    maps: CollectionProperty(
        type=UBK_Map,
    )

    active_map_index: IntProperty(
        default=0,
    )


classes = (UBK_Object,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
