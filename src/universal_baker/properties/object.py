from __future__ import annotations
import bpy
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, PointerProperty, CollectionProperty, IntProperty
from .baker import UBK_Baker
from .packer import UBK_Packer


class UBK_SourceObject(PropertyGroup):
    """Source object property"""

    source: PointerProperty(name="Source Object", type=bpy.types.Object)


class UBK_Object(PropertyGroup):
    """Bake settings for one target object."""

    enabled: BoolProperty(
        default=True,
    )

    target: PointerProperty(
        name="Target",
        type=bpy.types.Object,
    )

    sources: CollectionProperty(type=UBK_SourceObject)

    bakers: CollectionProperty(
        type=UBK_Baker,
    )

    active_baker_index: IntProperty(
        default=0,
    )

    packers: CollectionProperty(type=UBK_Packer)
    active_packer_index: bpy.props.IntProperty(
        default=0,
    )


classes = (
    UBK_SourceObject,
    UBK_Object,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
