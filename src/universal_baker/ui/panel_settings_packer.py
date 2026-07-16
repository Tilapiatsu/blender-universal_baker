from __future__ import annotations
from typing import Callable

import bpy

from ..core.controller import BakeController
from .panel_settings_output import (
    draw_output_settings,
)


def grid_layout(layout, alignment, size):
    row = layout.row()
    row.alignment = alignment
    row.ui_units_x = size
    return row


# -------------------------------------------------------------------------
# Draw Settings Functions
# -------------------------------------------------------------------------


def draw_pack_settings(self, context, draw: Callable):
    project = BakeController.project(context)
    if project is None:
        return

    active_pack = BakeController.active_packer(context)
    if active_pack is None:
        return

    layout = self.layout

    if active_pack.override_settings_pack:
        settings_pack = active_pack.settings_pack
    else:
        settings_pack = project.settings_pack
        layout.enabled = False

    draw(layout, settings_pack)


# -------------------------------------------------------------------------
# Main Settings Panel
# -------------------------------------------------------------------------


class UBK_UL_PackersPanel:
    """Packers Main panel."""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Universal Baker"


class UBK_UL_PackerPanel(UBK_UL_PackersPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_packer_panel"
    bl_label = "Packers"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):

        project = BakeController.project(context)
        if project is None:
            return

        layout = self.layout
        box = layout.box()
        # header = box.row()
        # box.use_property_split = True
        # box.use_property_decorate = False

        box.template_list("UBK_UL_PackList", "", project, "packers", project, "active_packer_index", rows=5)

        row = box.row(align=True)
        row.operator("ubk.add_packer", text="Add Packer", icon="ADD")
        row.operator("ubk.remove_packer", text="", icon="REMOVE")


# -------------------------------------------------------------------------
# Packer Settings Panel
# -------------------------------------------------------------------------


class UBK_UL_PackerSettingsPanel(UBK_UL_PackersPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_settings_packer_panel"
    bl_label = "Settings"
    bl_parent_id = "UBK_PT_packer_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):

        project = BakeController.project(context)
        if project is None:
            return

        layout = self.layout
        box = layout.box()
        header = box.row()
        box.use_property_split = True
        box.use_property_decorate = False

        active_packer = BakeController.active_packer(context)

        if active_packer is None:
            header.label(text="Add a Packer.", icon="INFO")
            return

        box.prop(active_packer, "image_name")
        if len(active_packer.mappings) != 4:
            box.label(text="Invalid Mapping.", icon="WARNING")
            box.operator("ubk.packer_mapping_fix", icon="MODIFIER")
            return

        red = active_packer.mappings[0]
        green = active_packer.mappings[1]
        blue = active_packer.mappings[2]
        alpha = active_packer.mappings[3]

        col1 = box.column(align=True)
        col2 = box.column(align=True)
        col3 = box.column(align=True)
        col4 = box.column(align=True)
        col5 = box.column(align=True)

        row1 = col1.row()
        row2 = col2.row()

        grid_layout(row1, alignment="CENTER", size=4).prop(red, "enabled", text="R")
        grid_layout(row1, alignment="CENTER", size=4).prop(green, "enabled", text="G")
        grid_layout(row1, alignment="CENTER", size=4).prop(blue, "enabled", text="B")
        grid_layout(row1, alignment="CENTER", size=4).prop(alpha, "enabled", text="A")

        grid_layout(row2, alignment="CENTER", size=4).label(text="_____")
        grid_layout(row2, alignment="CENTER", size=4).label(text="_____")
        grid_layout(row2, alignment="CENTER", size=4).label(text="_____")
        grid_layout(row2, alignment="CENTER", size=4).label(text="_____")

        grid_layout(col3, alignment="CENTER", size=4).prop(red, "source_map", text="Map")
        grid_layout(col3, alignment="CENTER", size=4).prop(green, "source_map", text="Map")
        grid_layout(col3, alignment="CENTER", size=4).prop(blue, "source_map", text="Map")
        grid_layout(col3, alignment="CENTER", size=4).prop(alpha, "source_map", text="Map")

        grid_layout(col4, alignment="CENTER", size=4).prop(red, "source_channel")
        grid_layout(col4, alignment="CENTER", size=4).prop(green, "source_channel")
        grid_layout(col4, alignment="CENTER", size=4).prop(blue, "source_channel")
        grid_layout(col4, alignment="CENTER", size=4).prop(alpha, "source_channel")

        # grid_layout(col4, alignment="CENTER", size=4).prop(red, "destination_channel")
        # grid_layout(col4, alignment="CENTER", size=4).prop(green, "destination_channel")
        # grid_layout(col4, alignment="CENTER", size=4).prop(blue, "destination_channel")
        # grid_layout(col4, alignment="CENTER", size=4).prop(alpha, "destination_channel")


# --------------------------------------------------------------------------
# Packer output Settings Panel
# -------------------------------------------------------------------------


class UBK_UL_PackerSettingsOutputPanel(UBK_UL_PackersPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_settings_bake_panel"
    bl_label = "Output"
    bl_parent_id = "UBK_PT_packer_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):

        project = BakeController.project(context)
        if project is None:
            return

        layout = self.layout
        box = layout.box()
        header = box.row()
        box.use_property_split = True
        box.use_property_decorate = False

        active_packer = BakeController.active_packer(context)

        if active_packer is None:
            header.label(text="Add a Packer.", icon="INFO")
            return

        layout.prop(active_packer, "override_settings_pack", toggle=1)
        if active_packer.override_settings_pack:
            box.label(text=f"{active_packer.image_name} settings")
        else:
            box.label(text="Inherited from Global Settings")

        draw_pack_settings(self, context, draw_output_settings)


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
