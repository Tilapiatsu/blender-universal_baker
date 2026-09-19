from __future__ import annotations

from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatVectorProperty,
    IntProperty,
)
from bpy.types import PropertyGroup

from ..services.visualization_bake import update_visualization
from ..services.visualization_cage import update_cage_color, update_edit_cage


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

    cage_edit: BoolProperty(name="Edit Cage", default=False, update=update_edit_cage)
    skew_edit: BoolProperty(name="Edit Skew", default=False)

    baker_idx: IntProperty(default=0)
    refreshing: BoolProperty(default=False)
    # is is_dragging allow to make custom bakers parameter clamping works
    is_dragging: BoolProperty(default=False)

    cage_color: FloatVectorProperty(
        name="Cage Color",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=[
            0.05,
            0.65,
            1.0,
            0.25,
        ],
        update=update_cage_color,
    )


classes = (UBK_Visualization,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
