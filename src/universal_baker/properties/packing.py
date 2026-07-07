from bpy.types import PropertyGroup
from bpy.props import EnumProperty, PointerProperty
from .map import UBK_Map


def get_packing_types(self, context):
    return [("R+G+B", "R+G+B", ""), ("RGB+A", "RGB+A", ""), ("R+G+B+A", "R+G+B+A", "")]


class UBK_Packing(PropertyGroup):
    packing_type: EnumProperty(items=get_packing_types)
    pack_r: PointerProperty(type=UBK_Map)
    pack_g: PointerProperty(type=UBK_Map)
    pack_b: PointerProperty(type=UBK_Map)
    pack_a: PointerProperty(type=UBK_Map)
    pack_rgb: PointerProperty(type=UBK_Map)


classes = (UBK_Packing,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
