from __future__ import annotations

import bpy

from bpy.types import PropertyGroup
from bpy.props import EnumProperty, StringProperty, IntProperty, BoolProperty

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

    export_file: BoolProperty(name="Export File", default=True)
    # TODO : add dynamic description to get and explain the registered tokens and transforms
    output_path: StringProperty(name="Output Path", default="//baking", subtype="FILE_PATH")
    filename_template: StringProperty(name="Filename", default="{object}_{image_name}")


classes = (UBK_Output,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
