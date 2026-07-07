from bpy.types import PropertyGroup, CollectionProperty, IntProperty, PointerProperty
from .object import UBK_Object
from .output import UBK_Output


class UBK_Project(PropertyGroup):
    objects: CollectionProperty(type=UBK_Object)
    output: PointerProperty(type=UBK_Output)


classes = (UBK_Project,)


def register():

    bpy.types.Scene.ubk_project = PointerProperty(type=UBK_Project)

    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.ubk_project
