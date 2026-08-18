from __future__ import annotations

from bpy.props import (
    BoolProperty,
    EnumProperty,
    IntProperty,
)
from bpy.types import PropertyGroup

from ..services.bake_visualization import update_visualization


class UBK_Visualization(PropertyGroup):
    """
    User-facing configuration for Universal Baker visualization.

    This contains persistent project settings only.

    Runtime Blender state is stored separately in
    runtime.visualization_state.
    """

    enabled_preview: BoolProperty(
        name="Enable Preview",
        description="Preview the result of the active baker",
        default=False,
        update=update_visualization,
    )

    enabled_display: BoolProperty(
        name="Enable Preview",
        description="Display the baked map for the active baker",
        default=False,
        update=update_visualization,
    )

    mode: EnumProperty(
        name="Mode",
        description="Visualization mode",
        items=[
            (
                "NONE",
                "None",
                "Preview and Display are Disabled",
            ),
            (
                "PREVIEW",
                "Preview",
                "Preview the active baker using the Cycles renderer",
            ),
            (
                "DISPLAY",
                "Display",
                "Display the latest baked result",
            ),
        ],
        default="NONE",
    )
    baker_idx: IntProperty(default=0)


classes = (UBK_Visualization,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
