from __future__ import annotations
from typing import Callable

import bpy

from ..core.controller import BakeController
from .panel import bake_group_needed, UBK_PT_MainPanel


# -------------------------------------------------------------------------
# Main Settings Panel
# -------------------------------------------------------------------------


class UBK_UL_BakeGroupSettingsPanel(UBK_PT_MainPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_bake_group_panel"
    bl_label = ""
    bl_parent_id = "UBK_PT_BakeGroupPanel"
    bl_options = {"DEFAULT_CLOSED"}

    @bake_group_needed
    def draw_header(self, context):
        layout = self.layout
        active_bake_group = BakeController.active_bake_group(context)

        layout.label(text=f"{active_bake_group.name} Settings", icon="OUTLINER")

    @bake_group_needed
    def draw(self, context):
        layout = self.layout
        box = layout.box()

        active_bake_group = BakeController.active_bake_group(context)

        box.prop(active_bake_group, "detect_udim", toggle=1)


classes = (UBK_UL_BakeGroupSettingsPanel,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
