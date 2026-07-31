from __future__ import annotations

import bpy

from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty,
    EnumProperty,
    IntProperty,
    CollectionProperty,
    PointerProperty,
)
from ..enum.channels import CHANNEL_ITEMS


ARTIFACT_TYPES = [
    ("BAKE", "Bake", ""),
    ("ACCUMULATED", "Accumulated", ""),
    ("PACK", "Packed", ""),
]


class UBK_ArtifactDependency(PropertyGroup):
    """
    Stores a dependency to another artifact.
    """

    uuid: StringProperty()


class UBK_ProducerUUID(PropertyGroup):
    uuid: StringProperty()


class UBK_ChannelMapping(PropertyGroup):
    channel: EnumProperty(
        name="SRC",
        items=CHANNEL_ITEMS,
        default="R",
    )


class UBK_Artifact(PropertyGroup):
    """
    Persistent description of one generated output.

    This PropertyGroup is intentionally lightweight.
    Image pixels are never stored here.
    """

    uuid: StringProperty()
    name: StringProperty()
    type: EnumProperty(
        items=ARTIFACT_TYPES,
        default="BAKE",
    )

    bake_group_uuid: StringProperty()
    producer_uuid: StringProperty()
    target_object_uuid: StringProperty()
    relative_path: StringProperty()
    filename: StringProperty()
    extension: StringProperty()
    width: IntProperty()
    height: IntProperty()
    channels: IntProperty(
        default=4,
    )
    color_space: StringProperty()
    file_format: StringProperty()
    checksum: StringProperty()
    created: StringProperty()
    dependencies: CollectionProperty(
        type=UBK_ArtifactDependency,
    )
    dependencies_mapping: CollectionProperty(type=UBK_ChannelMapping)


classes = (
    UBK_ChannelMapping,
    UBK_ArtifactDependency,
    UBK_ProducerUUID,
    UBK_Artifact,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
