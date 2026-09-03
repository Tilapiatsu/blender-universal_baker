from __future__ import annotations

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import PropertyGroup

from .settings_cage import UBK_CageSettings


def get_uv_layer(self, context, edit_text):
    return [uv.name for uv in self.object.data.uv_layers]


class UBK_SourceObject(PropertyGroup):
    """Source object property"""

    enabled: BoolProperty(
        default=True,
    )

    object: PointerProperty(name="Source Object", type=bpy.types.Object)


class UBK_TargetObject(PropertyGroup):
    """Bake settings for one target object."""

    uuid: StringProperty()

    enabled: BoolProperty(
        default=True,
    )

    object: PointerProperty(
        name="Target",
        type=bpy.types.Object,
    )

    image: PointerProperty(type=bpy.types.Image)

    source_objects: CollectionProperty(type=UBK_SourceObject)
    active_source_object_index: IntProperty(default=0)
    uv_layer: StringProperty(
        name="UV Map", description="UV layer used for baking", default="UVMap", search=get_uv_layer
    )

    settings_cage: PointerProperty(type=UBK_CageSettings)

    @property
    def use_cage(self) -> bool:
        return self.cage_mode != "NONE"


classes = (
    UBK_SourceObject,
    UBK_TargetObject,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
