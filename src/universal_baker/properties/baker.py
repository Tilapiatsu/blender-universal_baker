from __future__ import annotations
import bpy
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, EnumProperty, StringProperty, PointerProperty
from .settings_bake import UBK_BakeSettings


def bake_map_items(self, context):
    from ..core.registry_baker import registry_baker

    return registry_baker.enum_items()


class UBK_Baker(PropertyGroup):
    """One Bake Map"""

    uuid: StringProperty()

    enabled: BoolProperty(
        name="Enabled",
        default=True,
    )

    baker: EnumProperty(
        name="Bake Type",
        items=bake_map_items,
    )

    image_name: StringProperty(
        name="Image Name",
        default="Bake",
    )

    image: PointerProperty(
        type=bpy.types.Image,
    )

    override_settings: BoolProperty(
        name="Override Settings",
        default=False,
    )

    settings: PointerProperty(
        type=UBK_BakeSettings,
    )

    override_settings_cage: BoolProperty(
        name="Override Cage",
        default=False,
    )


classes = (UBK_Baker,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
