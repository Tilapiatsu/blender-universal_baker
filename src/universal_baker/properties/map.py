from __future__ import annotations
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, EnumProperty, StringProperty, PointerProperty
from .settings_cage import UBK_CageSettings
from .settings_bake import UBK_BakeSettings


def bake_map_items(self, context):
    """Dynamic enum.

    Later this will query the Baker Registry.
    """

    return [
        ("DIFFUSE", "Diffuse", ""),
    ]


class UBK_Map(PropertyGroup):
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

    override_settings_bake: BoolProperty(
        name="Override Bake Settings",
        default=False,
    )

    settings_bake: PointerProperty(
        type=UBK_BakeSettings,
    )

    override_settings_cage: BoolProperty(
        name="Override Cage",
        default=False,
    )

    settings_cage: PointerProperty(
        type=UBK_CageSettings,
    )


classes = (UBK_Map,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
