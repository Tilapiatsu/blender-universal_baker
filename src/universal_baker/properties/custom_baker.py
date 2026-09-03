from __future__ import annotations

from bpy.props import (
    CollectionProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import PropertyGroup

from .baker_parameter import UBK_BakerParameterValue

"""
Stores the user values of a specific custom baker. this values will be passed to the baker and to the visualization
system to make sure they produce the desired result
"""


class UBK_CustomBaker(PropertyGroup):
    asset_id: StringProperty(name="Asset ID")

    asset_version: IntProperty(name="Asset Version", default=1)

    parameters: CollectionProperty(type=UBK_BakerParameterValue)


classes = (UBK_CustomBaker,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
