from __future__ import annotations

import bpy

from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty,
    EnumProperty,
    IntProperty,
    CollectionProperty,
)


ARTIFACT_TYPES = [
    ("BAKE", "Bake", ""),
    ("ACCUMULATED", "Accumulated", ""),
    ("PACK", "Packed", ""),
]


class UBK_ArtifactDependency(PropertyGroup):
    """
    Stores a dependency to another artifact.
    """

    artifact_uid: StringProperty()


class UBK_Artifact(PropertyGroup):
    """
    Persistent description of one generated output.

    This PropertyGroup is intentionally lightweight.
    Image pixels are never stored here.
    """

    uuid: StringProperty()

    type: EnumProperty(
        items=ARTIFACT_TYPES,
        default="BAKE",
    )

    target_uid: StringProperty()
    producer_id: StringProperty()
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


classes = (
    UBK_ArtifactDependency,
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
