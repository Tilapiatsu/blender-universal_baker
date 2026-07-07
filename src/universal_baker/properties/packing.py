from bpy.types import PropertyGroup, BoolProperty, EnumProperty, StringProperty, IntProperty, PointerProperty
from .map import UB_Map


class UBK_Packing(PropertyGroup):
    packing_type: EnumProperty(items=get_packing_types)
    pack_r: PointerProperty(type=UB_Map)
    pack_g: PointerProperty(type=UB_Map)
    pack_b: PointerProperty(type=UB_Map)
    pack_a: PointerProperty(type=UB_Map)
    pack_rgb: PointerProperty(type=UB_Map)


classes = (UBK_Packing,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
