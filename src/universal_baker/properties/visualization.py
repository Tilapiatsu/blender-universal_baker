from __future__ import annotations

from bpy.props import (
    BoolProperty,
    EnumProperty,
)
from bpy.types import PropertyGroup

from ..services.bake_visualization import BakeVisualizationService


def update_visualization(self, context):
    from ..core.controller import BakeController

    if not self.enabled:
        BakeVisualizationService.disable()
        return

    baker = BakeController.active_baker(context)

    if baker is None:
        return

    if self.mode == "PREVIEW":
        BakeVisualizationService.enable_preview(baker)

    elif self.mode == "DISPLAY":
        # Later resolved through OutputProvider.
        ...


class UBK_Visualization(PropertyGroup):
    """
    User-facing configuration for Universal Baker visualization.

    This contains persistent project settings only.

    Runtime Blender state is stored separately in
    runtime.visualization_state.
    """

    enabled: BoolProperty(
        name="Visualization",
        description="Enable Universal Baker bake visualization",
        default=False,
        update=update_visualization,
    )

    mode: EnumProperty(
        name="Mode",
        description="Visualization mode",
        items=[
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
        default="PREVIEW",
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
