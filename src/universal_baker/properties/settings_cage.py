from __future__ import annotations

from bpy.props import EnumProperty, FloatProperty, PointerProperty, StringProperty
from bpy.types import Image, Object, PropertyGroup


class UBK_CageSettings(PropertyGroup):
    cage_mode: EnumProperty(
        name="Mode",
        items=[
            ("NONE", "None", "Without Cage."),
            ("OBJECT", "Object", "Specify an object as the cage"),
            ("GENERATED", "Generated", "Automatically generate Cage by offsetting vertices along normal"),
        ],
        default="NONE",
    )
    # TODO: Need to make it compatible with "NONE", "GENERATED" and "OBJECT" : It will be convenient to visualize Cage
    # regardless of the context.
    # It may be great to simplify : we certainly don't need 3 cases :
    # - By default custom cages is set, we can just use the extrusion parameter which offset the vertices -> A cage is
    # created for display purpose, and then stash afterward
    # - The user can the choose to "edit_cage" to paint the distance using weight paint mode -> the Cage object is now
    # kept but unlinked from the scene when the edit cage is disabled

    # TODO: Need to prevent to load the same object as the target object
    cage_object_custom: PointerProperty(
        name="Cage Object",
        type=Object,
    )
    cage_object_generated: PointerProperty(
        name="Genertated Cage Object",
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

    @property
    def cage_object(self) -> Object | None:
        match self.cage_mode:
            case "OBJECT":
                return self.cage_object_custom
            case "GENERATED":
                return self.cage_object_generated
            case _:
                return None


classes = (UBK_CageSettings,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
