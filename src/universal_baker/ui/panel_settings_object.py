from __future__ import annotations
from typing import Callable

import bpy

from ..core.controller import BakeController
from .panel import object_needed, UBK_PT_MainPanel


# -------------------------------------------------------------------------
# Main Settings Panel
# -------------------------------------------------------------------------


class UBK_UL_TargetObjectSettingsPanel(UBK_PT_MainPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_target_object_panel"
    bl_label = ""
    bl_parent_id = "UBK_PT_ObjectPanel"
    bl_options = {"DEFAULT_CLOSED"}

    @object_needed
    def draw_header(self, context):
        layout = self.layout
        active_object = BakeController.active_object(context)

        layout.label(text=f"{active_object.object.name} Settings", icon="OBJECT_DATAMODE")

    @object_needed
    def draw(self, context):
        layout = self.layout
        box = layout.box()

        active_object = BakeController.active_object(context)

        box.prop(active_object, "detect_udim", toggle=1)
        box.prop(active_object, "uv_layer")


classes = (UBK_UL_TargetObjectSettingsPanel,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
