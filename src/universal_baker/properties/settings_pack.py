from __future__ import annotations

import bpy
from ..services.internal_data import InternalDataService
from .settings_base import get_colorspace_items


class UBK_PackSettings(bpy.types.PropertyGroup):
    internal_name: bpy.props.StringProperty(default="Default")

    # -------------------------------------------------------------------------
    # Image
    # -------------------------------------------------------------------------

    resolution_x: bpy.props.IntProperty(
        name="Width",
        default=2048,
        min=1,
        subtype="PIXEL",
    )

    resolution_y: bpy.props.IntProperty(
        name="Height",
        default=2048,
        min=1,
        subtype="PIXEL",
    )

    colorspace: bpy.props.EnumProperty(
        name="Colorspace",
        items=get_colorspace_items,
    )

    @property
    def file_format_settings(self):
        node = InternalDataService.get_output_node(self.internal_name)
        if node is None:
            return

        return node.format


classes = (UBK_PackSettings,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
