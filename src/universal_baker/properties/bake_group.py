from __future__ import annotations

import bpy

from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty,
    BoolProperty,
    CollectionProperty,
    PointerProperty,
    IntProperty,
)

from .object import UBK_TargetObject
from .baker import UBK_Baker
from .packer import UBK_Packer
from .settings_bake import UBK_BakeSettings
from ..services.bake_visualization import update_visualization


class UBK_BakeGroup(PropertyGroup):
    """Bake target contains all properties for one group of target objects."""

    uuid: StringProperty(name="uuid", default="")
    enabled: BoolProperty(
        name="Enabled",
        default=True,
    )

    name: StringProperty(
        name="Target",
        default="Group",
    )

    expanded: BoolProperty(default=True)

    detect_udim: BoolProperty(
        name="Detect UDIM",
        default=False,
    )

    target_objects: CollectionProperty(type=UBK_TargetObject)

    active_target_object_index: IntProperty(default=0)

    bakers: CollectionProperty(type=UBK_Baker)
    active_baker_index: IntProperty(
        update=update_visualization,
    )

    packers: CollectionProperty(type=UBK_Packer)
    active_packer_index: bpy.props.IntProperty(
        default=0,
    )

    override_settings: BoolProperty(
        name="Override Settings",
        default=False,
    )

    settings: PointerProperty(
        type=UBK_BakeSettings,
    )


classes = (UBK_BakeGroup,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
