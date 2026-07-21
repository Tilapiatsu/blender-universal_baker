from __future__ import annotations

import bpy
from ..services.internal_data import InternalDataService
from .settings_output import UBK_Output
from .settings_base import UBK_Settings


class UBK_BakeSettings(UBK_Settings, UBK_Output):
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
