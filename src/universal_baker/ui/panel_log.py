from __future__ import annotations

import bpy
from bpy.types import Panel

from ..constant import ICON_LOGGER, LOG_RUNTIME
from ..logger.blender import draw_logger_panel


class UBK_PT_Logger(Panel):
    bl_idname = "UBK_PT_logger"
    bl_label = ""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Universal Baker"

    bl_order = 100

    @classmethod
    def poll(cls, context):
        return LOG_RUNTIME is not None

    def draw_header(self, context):
        layout = self.layout

        layout.label(text="Execution Progress", icon=ICON_LOGGER)

    def draw(self, context):
        layout = self.layout
        ui_sink = LOG_RUNTIME.ui_sink
        if ui_sink is None:
            self.layout.label(text="Logger unavailable")
            return

        draw_logger_panel(
            layout,
            context,
            LOG_RUNTIME,
        )


classes = (UBK_PT_Logger,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
