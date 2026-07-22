from __future__ import annotations
import bpy
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, PointerProperty, CollectionProperty, IntProperty


class UBK_SourceObject(PropertyGroup):
    """Source object property"""

    enabled: BoolProperty(
        default=True,
    )

    source: PointerProperty(name="Source Object", type=bpy.types.Object)


class UBK_TargetObject(PropertyGroup):
    """Bake settings for one target object."""

    enabled: BoolProperty(
        default=True,
    )

    target: PointerProperty(
        name="Target",
        type=bpy.types.Object,
    )

    sources: CollectionProperty(type=UBK_SourceObject)
    active_source_index: IntProperty(default=0)

    use_cage: BoolProperty(
        name="Use Cage",
        default=False,
    )
    cache_object: PointerProperty(name="Cage Object", type=bpy.types.Object)


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
