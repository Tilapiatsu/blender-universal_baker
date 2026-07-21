from __future__ import annotations

import bpy

from bpy.types import PropertyGroup
from bpy.props import EnumProperty, StringProperty, IntProperty
from ..services.internal_data import InternalDataService

from .settings_base import get_colorspace_items


class UBK_Output(PropertyGroup):
    # -------------------------------------------------------------------------
    # Image
    # -------------------------------------------------------------------------

    resolution_x: IntProperty(
        name="Width",
        default=2048,
        min=1,
        subtype="PIXEL",
    )

    resolution_y: IntProperty(
        name="Height",
        default=2048,
        min=1,
        subtype="PIXEL",
    )

    # -------------------------------------------------------------------------
    # Color
    # -------------------------------------------------------------------------

    colorspace: EnumProperty(
        name="Colorspace",
        items=get_colorspace_items,
    )

    # -------------------------------------------------------------------------
    # Path
    # -------------------------------------------------------------------------

    output_path: StringProperty(name="Output Path", default="//", subtype="FILE_PATH")

    @property
    def file_format_settings(self):
        node = InternalDataService.get_output_node(self.internal_name)
        if node is None:
            return

        return node.format
