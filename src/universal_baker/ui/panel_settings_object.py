from __future__ import annotations

import bpy

from ..core.controller import BakeController
from .panel import UBK_PT_MainPanel, object_needed

# -------------------------------------------------------------------------
# Main Settings Panel
# -------------------------------------------------------------------------


class UBK_UL_TargetObjectSettingsPanel(UBK_PT_MainPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_target_object_panel"
    bl_label = ""
    bl_parent_id = "UBK_PT_TargetObjectPanel"
    bl_options = {"DEFAULT_CLOSED"}

    @object_needed
    def draw_header(self, context):
        layout = self.layout
        active_object = BakeController.active_target_object(context)

        layout.label(text=f"{active_object.object.name} Settings", icon="OBJECT_DATAMODE")

    @object_needed
    def draw(self, context):
        layout = self.layout
        box = layout.box()

        active_object = BakeController.active_target_object(context)

        box.prop(active_object, "uv_layer")

        box.separator()
        box.label(text="Source Objects :")
        box.template_list(
            "UBK_UL_SourceObjectList",
            "",
            active_object,
            "source_objects",
            active_object,
            "active_source_object_index",
            rows=5,
        )
        row = box.row(align=True)
        row.operator("ubk.add_source_object", text="Add Selected", icon="ADD")
        row.operator("ubk.remove_source_object", text="", icon="REMOVE")


classes = (UBK_UL_TargetObjectSettingsPanel,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
