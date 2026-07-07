import bpy
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, PointerProperty, CollectionProperty, IntProperty
from .map import UBK_Map


class UBK_Object(PropertyGroup):
    enabled: BoolProperty(default=True)
    target: PointerProperty(type=bpy.types.Object)
    maps: CollectionProperty(type=UBK_Map)
    active_map: IntProperty()


classes = (UBK_Object,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
