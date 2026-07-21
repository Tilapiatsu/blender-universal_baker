from __future__ import annotations
from typing import Callable

import bpy

from ..core.controller import BakeController
from .panel import (
    draw_baking_settings,
    draw_sampling_settings,
)

# -------------------------------------------------------------------------
# Draw Settings Functions
# -------------------------------------------------------------------------


def draw_global_output_settings(self, context, draw: Callable):
    project = BakeController.project(context)
    if project is None:
        return

    layout = self.layout

    settings_bake = project.settings_bake

    draw(layout, settings_bake)


# -------------------------------------------------------------------------
# Output Settings Panel
# -------------------------------------------------------------------------


def draw_output_settings(layout, settings):
    layout.use_property_split = True
    layout.use_property_decorate = False
    internal_data = BakeController.get_output_node(settings.internal_name)
    if internal_data is None:
        layout.label(text="Add a Target object and a Map first.", icon="INFO")
    else:
        layout.prop(settings, "resolution_x")
        layout.prop(settings, "resolution_y")
        layout.template_image_settings(internal_data.format, color_management=False)
        layout.prop(settings, "colorspace")
        layout.prop(settings, "output_path")


# -------------------------------------------------------------------------
# Global Main Settings Panel
# -------------------------------------------------------------------------


class UBK_UL_GlobalSettingsPanel:
    """Global Bake Settings panel."""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Universal Baker"


class UBK_PT_GlobalBakerSettingsPanel(UBK_UL_GlobalSettingsPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_global_settings_baker_panel"
    bl_label = ""
    bl_category = "Universal Baker"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Global Settings", icon="MODIFIER")

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        header = box.row()
        header.label(text="Baker inherits Gobal Settings by default.", icon="INFO")


# -------------------------------------------------------------------------
# Output Settings Panel
# -------------------------------------------------------------------------


class UBK_PT_GlobalBakerSettingsOutputPanel(UBK_UL_GlobalSettingsPanel, bpy.types.Panel):
    bl_parent_id = "UBK_PT_global_settings_baker_panel"
    bl_label = "Output"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        draw_global_output_settings(self, context, draw_output_settings)


# -------------------------------------------------------------------------
# Bake Settings Panel
# -------------------------------------------------------------------------


class UBK_PT_GlobalBakerSettingsBakingPanel(UBK_UL_GlobalSettingsPanel, bpy.types.Panel):
    bl_parent_id = "UBK_PT_global_settings_baker_panel"
    bl_label = "Baking"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        draw_global_output_settings(self, context, draw_baking_settings)


# -------------------------------------------------------------------------
# Sampling Settings Panel
# -------------------------------------------------------------------------


class UBK_PT_GlobalBakerSettingsSamplingPanel(UBK_UL_GlobalSettingsPanel, bpy.types.Panel):
    bl_parent_id = "UBK_PT_global_settings_baker_panel"
    bl_label = "Sampling"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        draw_global_output_settings(self, context, draw_sampling_settings)


classes = (
    UBK_PT_GlobalBakerSettingsPanel,
    UBK_PT_GlobalBakerSettingsBakingPanel,
    UBK_PT_GlobalBakerSettingsSamplingPanel,
    UBK_PT_GlobalBakerSettingsOutputPanel,
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
