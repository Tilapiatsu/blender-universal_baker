from __future__ import annotations

import uuid

import bpy

from bpy.types import PropertyGroup
from bpy.props import EnumProperty, PointerProperty, BoolProperty, StringProperty
from ..core import registry_baker
from .baker import UBK_Baker
from .settings_pack import UBK_PackerSettings
from ..packers.channels import CHANNEL_ITEMS


def get_source_bakers_items(self, context):
    items = [("NONE", "None", "")]

    from ..core.controller import BakeController

    active_object = BakeController.active_object(context)

    if active_object is None:
        return items

    for b in active_object.bakers:
        items.append((b.uuid, f"{b.baker}_{b.image_name}", ""))

    return items


class UBK_ChannelMapping(PropertyGroup):
    """Map one channel to another"""

    enabled: BoolProperty(name="Enabled", default=True)
    source_map_uuid: bpy.props.EnumProperty(
        name="Source Baker",
        items=get_source_bakers_items,
    )
    source_map: PointerProperty(type=UBK_Baker)
    source_channel: EnumProperty(
        name="SRC",
        items=CHANNEL_ITEMS,
        default="R",
    )
    destination_channel: EnumProperty(
        name="DST",
        items=CHANNEL_ITEMS,
        default="R",
    )


class UBK_Packer(PropertyGroup):
    """Packing settings from output maps"""

    # packer_type: EnumProperty(name="Packing Type", items=packer_types)
    uuid: bpy.props.StringProperty()
    packer: bpy.props.StringProperty(name="Packer")
    enabled: BoolProperty(name="Enabled", default=True)
    override_settings: BoolProperty(name="Override Settings", default=False)
    image_name: StringProperty(name="Name", default="Channel Packing")
    active_packer_index: bpy.props.IntProperty(default=0)
    mappings: bpy.props.CollectionProperty(type=UBK_ChannelMapping)
    settings: bpy.props.PointerProperty(type=UBK_PackerSettings)


classes = (
    UBK_ChannelMapping,
    UBK_Packer,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
