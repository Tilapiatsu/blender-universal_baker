from __future__ import annotations

import uuid

import bpy

from bpy.types import PropertyGroup
from bpy.props import EnumProperty, PointerProperty, BoolProperty, StringProperty
from .map import UBK_Map
from .settings_pack import UBK_PackSettings
from ..packing.channels import CHANNEL_ITEMS


def packing_types(self, context):
    return [("R+G+B", "R+G+B", ""), ("RGB+A", "RGB+A", ""), ("R+G+B+A", "R+G+B+A", "")]


class UBK_ChannelMapping(PropertyGroup):
    """Map one channel to another"""

    enabled: BoolProperty(name="Enabled", default=True)
    source_map_uuid: bpy.props.StringProperty()
    source_map: PointerProperty(type=UBK_Map)
    source_channel: EnumProperty(
        name="channel",
        items=CHANNEL_ITEMS,
        default="R",
    )
    destination_channel: EnumProperty(
        name="Destination",
        items=CHANNEL_ITEMS,
        default="R",
    )


class UBK_ChannelPacking(PropertyGroup):
    """Packing settings from output maps"""

    # packing_type: EnumProperty(name="Packing Type", items=packing_types)
    uuid: bpy.props.StringProperty()
    enabled: BoolProperty(name="Enabled", default=True)
    name: StringProperty(name="Name", default="Channel Packing")
    active_mapping_index: bpy.props.IntProperty(default=0)
    mappings: bpy.props.CollectionProperty(type=UBK_ChannelMapping)
    pack_settings: bpy.props.PointerProperty(type=UBK_PackSettings)


classes = (
    UBK_ChannelMapping,
    UBK_ChannelPacking,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
