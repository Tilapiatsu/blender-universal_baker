from __future__ import annotations
import bpy
from bpy.types import PropertyGroup
from bpy.props import CollectionProperty, PointerProperty
from .object import UBK_Object
from .settings_bake import UBK_BakeSettings
from .settings_cage import UBK_CageSettings
from .settings_pack import UBK_PackSettings


class UBK_Project(PropertyGroup):
    """Scene baking project."""

    project_name: bpy.props.StringProperty(
        name="Project Name",
        default="Bake Project",
    )
    objects: CollectionProperty(type=UBK_Object)
    active_object_index: bpy.props.IntProperty(
        default=0,
    )
    settings_bake: PointerProperty(type=UBK_BakeSettings)
    settings_cage: PointerProperty(type=UBK_CageSettings)


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
