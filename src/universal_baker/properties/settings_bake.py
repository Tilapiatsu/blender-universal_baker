from __future__ import annotations

import bpy
from ..services.internal_data import InternalDataService
from .settings_base import get_colorspace_items


def get_color_depth(self, context):
    items = []
    if self.file_format in ["PNG", "TIFF", "TARGA"]:
        items.append(
            ("8", "8", ""),
        )
        items.append(
            ("16", "16", ""),
        )
    elif self.file_format in ["OPEN_EXR"]:
        items.append(
            ("16", "16", ""),
        )
        items.append(
            ("32", "32", ""),
        )
    elif self.file_format in ["DPX"]:
        items.append(
            ("8", "8", ""),
        )
        items.append(
            ("10", "10", ""),
        )
        items.append(
            ("12", "12", ""),
        )
        items.append(
            ("16", "16", ""),
        )
    elif self.file_format in ["JPEG", "BMP", "CINEON"]:
        items.append(
            ("8", "8", ""),
        )

    return items


class UBK_BakeSettings(bpy.types.PropertyGroup):
    internal_name: bpy.props.StringProperty(default="Default")

    inherit: bpy.props.BoolProperty(
        name="Inherit Global Settings",
        default=True,
    )
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

    # -------------------------------------------------------------------------
    # Bake
    # -------------------------------------------------------------------------

    use_multires: bpy.props.BoolProperty(
        name="Bake From Multires",
        default=False,
    )

    margin: bpy.props.IntProperty(
        name="Margin",
        default=16,
        min=0,
        subtype="PIXEL",
    )

    margin_type: bpy.props.EnumProperty(
        name="Margin Type",
        items=[
            ("ADJACENT_FACES", "Adjacent Faces", ""),
            ("EXTEND", "Extend", ""),
        ],
        default="ADJACENT_FACES",
    )

    target: bpy.props.EnumProperty(
        name="Target",
        items=[
            ("IMAGE_TEXTURES", "Image Testures", ""),
            ("VERTEX_COLORS", "Active Color Attribute", ""),
        ],
    )

    use_clear: bpy.props.BoolProperty(
        name="Clear Image",
        default=True,
    )

    # -------------------------------------------------------------------------
    # Sampling
    # -------------------------------------------------------------------------

    adaptive_sampling: bpy.props.BoolProperty(
        name="Adaptive Sampling",
        default=False,
    )

    samples: bpy.props.IntProperty(
        name="Samples",
        default=64,
        min=1,
    )

    noise_threshold: bpy.props.FloatProperty(
        name="Noise Threashold",
        default=0.01,
        min=0,
    )

    min_samples: bpy.props.IntProperty(
        name="Min Samples",
        default=0,
        min=0,
    )

    max_samples: bpy.props.IntProperty(
        name="Max Samples",
        default=512,
        min=1,
    )

    denoise: bpy.props.BoolProperty(
        name="Denoise",
        default=False,
    )

    # -------------------------------------------------------------------------
    # Color
    # -------------------------------------------------------------------------

    # colorspace: bpy.props.StringProperty(
    #     default="sRGB",
    # )
    colorspace: bpy.props.EnumProperty(
        items=get_colorspace_items,
    )

    @property
    def file_format_settings(self):
        node = InternalDataService.get_output_node(self.internal_name)
        if node is None:
            return

        return node.format


classes = (UBK_BakeSettings,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
