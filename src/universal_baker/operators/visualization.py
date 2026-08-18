from __future__ import annotations

import bpy

from ..constant import LOG
from ..services.bake_visualization import BakeVisualizationService
from ..core.controller import BakeController
from ..core.registry_baker import registry_baker


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
        bake_group = BakeController.active_bake_group(context)

        if bake_group is None:
            LOG.warning("Bake Group not found")
            return

        baker = BakeController.active_baker(context)

        if baker is None:
            LOG.warning("Baker not found")
            return

        if mode == "PREVIEW":
            producer = registry_baker[baker.baker]
            BakeVisualizationService.enable_preview(producer)

        elif mode == "DISPLAY":
            BakeVisualizationService.enable_display(bake_group.uuid, baker.accumulated_uuid)


classes = (UBK_OT_VisualizationToggle,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
