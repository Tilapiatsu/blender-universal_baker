from __future__ import annotations
from typing import Callable

import bpy

from ..core.controller import BakeController

# -------------------------------------------------------------------------
# Draw Settings Functions
# -------------------------------------------------------------------------


def draw_map_settings(self, context, draw: Callable):
    project = BakeController.project(context)
    if project is None:
        return

    active_map = BakeController.active_map(context)
    if active_map is None:
        return

    layout = self.layout

    if active_map.override_bake_settings:
        bake_settings = active_map.bake_settings
    else:
        bake_settings = project.bake_settings
        layout.enabled = False

    draw(layout, bake_settings)


def draw_global_settings(self, context, draw: Callable):
    project = BakeController.project(context)
    if project is None:
        return

    layout = self.layout

    bake_settings = project.bake_settings

    draw(layout, bake_settings)


# -------------------------------------------------------------------------
# Main Settings Panel
# -------------------------------------------------------------------------


class UBK_UL_SettingsPanel:
    """Bake Settings panel."""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Universal Baker"


class UBK_UL_BakeSettingsPanel(UBK_UL_SettingsPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_bake_settings_panel"
    bl_label = "Map Bake Settings"

    def draw(self, context):

        project = BakeController.project(context)
        if project is None:
            return

        layout = self.layout
        box = layout.box()
        header = box.row()
        box.use_property_split = True
        box.use_property_decorate = False

        active_object = BakeController.active_object(context)

        if active_object is None:
            header.label(text="Add a target Object.", icon="INFO")
            return

        active_map = BakeController.active_map(context)
        if active_map is None:
            header.label(text="Add a Bake Map.", icon="INFO")
            return

        box.prop(active_map, "image_name")
        layout.prop(active_map, "override_bake_settings", toggle=1)
        if active_map.override_bake_settings:
            box.label(text=f"{active_object.target.name}_{active_map.image_name} settings")
        else:
            box.label(text="Inherited from Global Settings")


# -------------------------------------------------------------------------
# Global Main Settings Panel
# -------------------------------------------------------------------------


class UBK_UL_GlobalSettingsPanel:
    """Global Bake Settings panel."""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Universal Baker"


class UBK_UL_GlobalBakeSettingsPanel(UBK_UL_GlobalSettingsPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_global_bake_settings_panel"
    bl_label = "Global Bake Settings"
    bl_category = "Universal Baker"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        header = box.row()
        header.label(text="Maps inherits Gobal Settings by default.", icon="INFO")


# -------------------------------------------------------------------------
# Output Settings Panel
# -------------------------------------------------------------------------


def draw_output_settings(layout, bake_settings):
    layout.use_property_split = True
    layout.use_property_decorate = False
    internal_data = BakeController.get_output_node(bake_settings.internal_name)
    if internal_data is None:
        layout.label(text="Add a Target object and a Map first.", icon="INFO")
    else:
        layout.prop(bake_settings, "resolution_x")
        layout.prop(bake_settings, "resolution_y")
        layout.template_image_settings(internal_data.format, color_management=False)


class UBK_UL_BakeSettingsOutputPanel(UBK_UL_SettingsPanel, bpy.types.Panel):
    bl_parent_id = "UBK_PT_bake_settings_panel"
    bl_label = "Output"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        draw_map_settings(self, context, draw_output_settings)


class UBK_UL_GlobalBakeSettingsOutputPanel(UBK_UL_GlobalSettingsPanel, bpy.types.Panel):
    bl_parent_id = "UBK_PT_global_bake_settings_panel"
    bl_label = "Output"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        draw_global_settings(self, context, draw_output_settings)


# -------------------------------------------------------------------------
# Bake Settings Panel
# -------------------------------------------------------------------------


def draw_baking_settings(layout, bake_settings):
    layout.use_property_split = True
    layout.use_property_decorate = False

    internal_data = BakeController.get_output_node(bake_settings.internal_name)
    if internal_data is None:
        layout.label(text="Add a Target object and a Map first.", icon="INFO")
    else:
        layout.prop(bake_settings, "use_multires")
        layout.prop(bake_settings, "margin")
        layout.prop(bake_settings, "margin_type")
        layout.prop(bake_settings, "target")
        layout.prop(bake_settings, "use_clear")


class UBK_UL_BakeSettingsBakingPanel(UBK_UL_SettingsPanel, bpy.types.Panel):
    bl_parent_id = "UBK_PT_bake_settings_panel"
    bl_label = "Baking"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        draw_map_settings(self, context, draw_baking_settings)


class UBK_UL_GlobalBakeSettingsBakingPanel(UBK_UL_GlobalSettingsPanel, bpy.types.Panel):
    bl_parent_id = "UBK_PT_global_bake_settings_panel"
    bl_label = "Baking"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        draw_global_settings(self, context, draw_baking_settings)


# -------------------------------------------------------------------------
# Sampling Settings Panel
# -------------------------------------------------------------------------


def draw_sampling_settings(layout, bake_settings):
    layout.use_property_split = True
    layout.use_property_decorate = False

    internal_data = BakeController.get_output_node(bake_settings.internal_name)
    if internal_data is None:
        layout.label(text="Add a Target object and a Map first.", icon="INFO")
    else:
        layout.prop(bake_settings, "adaptive_sampling")
        if bake_settings.adaptive_sampling:
            layout.prop(bake_settings, "noise_threshold")
            layout.prop(bake_settings, "min_samples")
            layout.prop(bake_settings, "max_samples")
        else:
            layout.prop(bake_settings, "samples")
        # layout.prop(bake_settings, "denoise")


class UBK_UL_BakeSettingsSamplingPanel(UBK_UL_SettingsPanel, bpy.types.Panel):
    bl_parent_id = "UBK_PT_bake_settings_panel"
    bl_label = "Sampling"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        draw_map_settings(self, context, draw_sampling_settings)


class UBK_UL_GlobalBakeSettingsSamplingPanel(UBK_UL_GlobalSettingsPanel, bpy.types.Panel):
    bl_parent_id = "UBK_PT_global_bake_settings_panel"
    bl_label = "Sampling"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        draw_global_settings(self, context, draw_sampling_settings)


classes = (
    UBK_UL_BakeSettingsPanel,
    UBK_UL_GlobalBakeSettingsPanel,
    UBK_UL_BakeSettingsBakingPanel,
    UBK_UL_BakeSettingsSamplingPanel,
    UBK_UL_BakeSettingsOutputPanel,
    UBK_UL_GlobalBakeSettingsBakingPanel,
    UBK_UL_GlobalBakeSettingsSamplingPanel,
    UBK_UL_GlobalBakeSettingsOutputPanel,
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
