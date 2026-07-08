from __future__ import annotations
from bpy.types import PropertyGroup
from bpy.props import EnumProperty, StringProperty, IntProperty


class UBK_Output(PropertyGroup):
    """Global output settings.

    These settings are inherited by every bake map unless
    explicitly overridden.
    """

    directory: StringProperty(
        name="Output Directory",
        subtype="DIR_PATH",
        default="//",
    )

    resolution_x: IntProperty(
        name="Width",
        default=2048,
        min=1,
    )

    resolution_y: IntProperty(
        name="Height",
        default=2048,
        min=1,
    )

    file_format: EnumProperty(
        name="Format",
        items=[
            ("PNG", "PNG", ""),
            ("OPEN_EXR", "OpenEXR", ""),
            ("TIFF", "TIFF", ""),
            ("JPEG", "JPEG", ""),
        ],
        default="PNG",
    )

    color_depth: EnumProperty(
        name="Depth",
        items=[
            ("8", "8", ""),
            ("16", "16", ""),
            ("32", "32", ""),
        ],
        default="8",
    )

    margin: IntProperty(
        name="Margin",
        default=16,
        min=0,
    )


classes = (UBK_Output,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
