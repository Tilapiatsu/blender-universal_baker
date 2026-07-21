from __future__ import annotations

import bpy
from universal_baker.properties.settings_base import UBK_Settings
from .settings_output import UBK_Output


class UBK_PackSettings(UBK_Settings, UBK_Output):
    internal_name: bpy.props.StringProperty(default="Default")


classes = (UBK_PackSettings,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
