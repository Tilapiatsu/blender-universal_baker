from __future__ import annotations

import bpy

from ..services.bake_visualization import BakeVisualizationService
from ..core.controller import BakeController


class UBK_OT_VisualizationToggle(bpy.types.Operator):
    bl_idname = "ubk.visualization_toggle"
    bl_label = "Toggle Visualization"

    def execute(self, context):

        project = context.scene.ubk_project

        settings = project.visualization

        if settings.enabled:
            settings.enabled = False

            BakeVisualizationService.disable()

        else:
            settings.enabled = True

            self._enable(
                context,
                settings.mode,
            )

        return {"FINISHED"}

    def _enable(self, context, mode):

        baker = BakeController.active_baker(context)

        if baker is None:
            return

        if mode == "PREVIEW":
            BakeVisualizationService.enable_preview(baker)

        elif mode == "DISPLAY":
            # TODO:
            # This will eventually use
            # OutputProvider.
            image = ...

            BakeVisualizationService.enable_display(image)


classes = (UBK_OT_VisualizationToggle,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
