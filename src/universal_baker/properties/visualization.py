from __future__ import annotations

from bpy.props import (
    BoolProperty,
    EnumProperty,
)
from bpy.types import PropertyGroup

from ..constant import LOG
from ..services.bake_visualization import BakeVisualizationService
from ..core.registry_baker import registry_baker


def update_visualization(self, context):
    from ..core.controller import BakeController

    # ISSUE: Switching active baker doesn't refresh the display
    if not self.enabled_preview and not self.enabled_display:
        self.mode = "NONE"
        BakeVisualizationService.disable()
        return

    bake_group = BakeController.active_bake_group(context)

    if bake_group is None:
        LOG.warning("Bake Gourp not found")
        return

    baker = BakeController.active_baker(context)

    if baker is None:
        LOG.warning("Baker not found")
        return

    if self.enabled_preview:
        self.enable_display = False
        self.mode = "PREVIEW"
        producer = registry_baker[baker.baker]
        BakeVisualizationService.enable_preview(producer)

    elif self.enabled_display:
        self.enable_preview = False
        self.mode = "DISPLAY"
        # ISSUE: querring accumulated_uuid from provider created a new empty image
        BakeVisualizationService.enable_display(bake_group.uuid, baker.accumulated_uuid)


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


classes = (UBK_Visualization,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
