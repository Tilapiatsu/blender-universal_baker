from __future__ import annotations

from bpy.props import BoolProperty
from bpy.types import PropertyGroup


class UBK_BakerSettings(PropertyGroup):
    baker_registered: BoolProperty(name="Bakers registered", default=False)


classes = (UBK_BakerSettings,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
