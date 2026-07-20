from __future__ import annotations
from typing import Callable

import bpy

from ..core.controller import BakeController
from .panel_settings_output import (
    draw_output_settings,
)
from .panel import object_needed, packer_needed, UBK_PT_MainPanel


def grid_layout(layout, alignment, size):
    row = layout.row()
    row.alignment = alignment
    row.ui_units_x = size
    return row


# -------------------------------------------------------------------------
# Draw Settings Functions
# -------------------------------------------------------------------------


def draw_pack_settings(layout, context, draw: Callable):
    project = BakeController.project(context)
    if project is None:
        return

    active_pack = BakeController.active_packer(context)
    if active_pack is None:
        return

    if active_pack.override_settings:
        settings_pack = active_pack.settings
    else:
        settings_pack = project.settings_pack
        layout.enabled = False

    draw(layout, settings_pack)


# -------------------------------------------------------------------------
# Main Settings Panel
# -------------------------------------------------------------------------


class UBK_UL_PackerPanel(UBK_PT_MainPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_packer_panel"
    bl_label = ""
    bl_parent_id = "UBK_PT_UniversalBakerPanel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Packers", icon="NODE_COMPOSITING")

    @object_needed
    def draw(self, context):
        layout = self.layout
        box = layout.box()

        active_object = BakeController.active_object(context)

        box.template_list("UBK_UL_PackList", "", active_object, "packers", active_object, "active_packer_index", rows=5)

        row = box.row(align=True)
        row.operator("ubk.add_packer", text="Add Packer", icon="ADD")
        row.operator("ubk.remove_packer", text="", icon="REMOVE")


# -------------------------------------------------------------------------
# Packer Settings Panel
# -------------------------------------------------------------------------


class UBK_UL_PackerSettingsPanel(UBK_PT_MainPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_settings_packer_panel"
    bl_label = "Packing"
    bl_parent_id = "UBK_PT_packer_panel"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return BakeController.active_packer(context) is not None

    @packer_needed
    def draw(self, context):
        layout = self.layout
        box = layout.box()

        active_packer = BakeController.active_packer(context)
        assert active_packer is not None

        box.prop(active_packer, "image_name")
        if len(active_packer.mappings) != 4:
            box.label(text="Invalid Mapping.", icon="STATUS_WARNING_FILLED")
            box.operator("ubk.packer_mapping_fix", icon="MODIFIER")
            return

        red = active_packer.mappings[0]
        green = active_packer.mappings[1]
        blue = active_packer.mappings[2]
        alpha = active_packer.mappings[3]

        main_row = box.row(align=True)
        col1 = main_row.column(align=True)
        main_row.separator()
        col2 = main_row.column(align=True)
        col3 = main_row.column(align=True)

        col1.ui_units_x = 1.5
        col1.alignment = "LEFT"
        col2.alignment = "RIGHT"
        col3.ui_units_x = 3
        col3.alignment = "RIGHT"

        col1.prop(red, "enabled", text="R", toggle=1)
        col1.prop(green, "enabled", text="G", toggle=1)
        col1.prop(blue, "enabled", text="B", toggle=1)
        col1.prop(alpha, "enabled", text="A", toggle=1)

        col2.prop(red, "source_map_uuid", text="Map")
        col2.prop(green, "source_map_uuid", text="Map")
        col2.prop(blue, "source_map_uuid", text="Map")
        col2.prop(alpha, "source_map_uuid", text="Map")

        col3.prop(red, "source_channel", text="")
        col3.prop(green, "source_channel", text="")
        col3.prop(blue, "source_channel", text="")
        col3.prop(alpha, "source_channel", text="")


# --------------------------------------------------------------------------
# Packer output Settings Panel
# -------------------------------------------------------------------------


class UBK_UL_PackerSettingsOutputPanel(UBK_PT_MainPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_settings_bake_panel"
    bl_label = "Output"
    bl_parent_id = "UBK_PT_packer_panel"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return BakeController.active_packer(context) is not None

    @packer_needed
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.use_property_split = True
        box.use_property_decorate = False

        active_packer = BakeController.active_packer(context)
        assert active_packer is not None

        layout.prop(active_packer, "override_settings", toggle=1)
        if active_packer.override_settings:
            box.label(text=f"{active_packer.image_name} settings")
        else:
            box.label(text="Inherited from Global Settings")

        col = layout.column(align=True)

        draw_pack_settings(col, context, draw_output_settings)


classes = (
    UBK_UL_PackerPanel,
    UBK_UL_PackerSettingsPanel,
    UBK_UL_PackerSettingsOutputPanel,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        print(cls)
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
