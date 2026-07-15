from __future__ import annotations

import bpy


class UBK_CageSettings(bpy.types.PropertyGroup):
    cage_object: bpy.props.PointerProperty(name="Cage Object", type=bpy.types.Object)

    mode: bpy.props.EnumProperty(
        name="Cage Mode",
        items=[("AUTO", "Auto", ""), ("BESPOKE", "Bespoke", "")],
    )

    extrusion: bpy.props.FloatProperty(
        name="Cage Extrusion",
        default=0.1,
        subtype="DISTANCE",
    )

    max_ray_distance: bpy.props.FloatProperty(
        name="Cage Max Ray Distance",
        description="The maximum ray distance for matching points between the active and selected objects. If zero, there is no limit.",
        default=0.0,
        subtype="DISTANCE",
    )


classes = (UBK_CageSettings,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
