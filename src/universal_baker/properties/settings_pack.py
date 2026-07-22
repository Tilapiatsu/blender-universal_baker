from __future__ import annotations

import bpy
from universal_baker.properties.settings_base import UBK_Settings
from .settings_output import UBK_Output


class UBK_PackerSettings(UBK_Settings):
    internal_name: bpy.props.StringProperty(default="Default")
    output_settings: bpy.props.PointerProperty(type=UBK_Output)


classes = (UBK_PackerSettings,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
