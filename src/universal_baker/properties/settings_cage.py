from __future__ import annotations

from bpy.props import EnumProperty, FloatProperty, StringProperty, PointerProperty
from bpy.types import Object, Image, PropertyGroup


class UBK_CageSettings(PropertyGroup):
    cage_mode: EnumProperty(
        name="Mode",
        items=[
            ("NONE", "None", "Without Cage."),
            ("OBJECT", "Object", "Specify an object as the cage"),
            ("AUTO", "Auto", "Automatically generate Cage by offsetting vertices along normal"),
        ],
        default="NONE",
    )
    cage_object: PointerProperty(
        name="Cage Object",
        type=Object,
    )
    cage_extrusion: FloatProperty(
        name="Cage Extrusion",
        default=0.1,
        min=0.0,
        subtype="DISTANCE",
    )
    max_ray_distance: FloatProperty(
        name="Max Ray Distance",
        default=0.0,
        min=0.0,
        subtype="DISTANCE",
        description="The maximum ray distance for matching points between the active and selected objects. If zero, there is no limit.",
    )
    extrusion_group: StringProperty(
        name="Extrusion Group",
        default="UBK_EXTRUSION_GROUP",
    )
    skew_map: PointerProperty(name="Skew Map", type=Image)


classes = (UBK_CageSettings,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
