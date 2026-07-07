import bpy
from bpy.types import PropertyGroup
from bpy.props import CollectionProperty, PointerProperty
from .object import UBK_Object
from .output import UBK_Output


class UBK_Project(PropertyGroup):
    objects: CollectionProperty(type=UBK_Object)
    output: PointerProperty(type=UBK_Output)


classes = (UBK_Project,)


def register():

    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.Scene.ubk_project = PointerProperty(type=UBK_Project)


def unregister():
    del bpy.types.Scene.ubk_project

    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
