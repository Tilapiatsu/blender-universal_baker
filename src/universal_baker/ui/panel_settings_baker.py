from __future__ import annotations
from typing import Callable

import bpy

from ..core.controller import BakeController
from .panel_settings_output import (
    draw_global_output_settings,
    draw_output_settings,
)
from .panel import baker_needed


def draw_map_settings(self, context, draw: Callable):
    project = BakeController.project(context)
    if project is None:
        return

    active_baker = BakeController.active_baker(context)
    if active_baker is None:
        return

    layout = self.layout

    if active_baker.override_settings:
        settings_bake = active_baker.settings_bake
    else:
        settings_bake = project.settings_bake
        layout.enabled = False

    draw(layout, settings_bake)


# -------------------------------------------------------------------------
# Main Settings Panel
# -------------------------------------------------------------------------


class UBK_UL_SettingsPanel:
    """Bake Settings panel."""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Universal Baker"


class UBK_UL_BakerSettingsPanel(UBK_UL_SettingsPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_settings_baker_panel"
    bl_label = "Map Baker Settings"

    @baker_needed
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.use_property_split = True
        box.use_property_decorate = False

        active_object = BakeController.active_object(context)
        assert active_object is not None

        active_baker = BakeController.active_baker(context)
        assert active_baker is not None

        box.prop(active_baker, "image_name")
        layout.prop(active_baker, "override_settings", toggle=1)
        if active_baker.override_settings:
            box.label(text=f"{active_object.target.name}_{active_baker.image_name} settings")
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


class UBK_UL_GlobalBakerSettingsPanel(UBK_UL_GlobalSettingsPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_global_settings_baker_panel"
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


class UBK_UL_BakerSettingsOutputPanel(UBK_UL_SettingsPanel, bpy.types.Panel):
    bl_parent_id = "UBK_PT_settings_baker_panel"
    bl_label = "Output"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        draw_map_settings(self, context, draw_output_settings)


class UBK_UL_GlobalBakerSettingsOutputPanel(UBK_UL_GlobalSettingsPanel, bpy.types.Panel):
    bl_parent_id = "UBK_PT_global_settings_baker_panel"
    bl_label = "Output"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        draw_global_output_settings(self, context, draw_output_settings)


# -------------------------------------------------------------------------
# Bake Settings Panel
# -------------------------------------------------------------------------


def draw_baking_settings(layout, settings_bake):
    layout.use_property_split = True
    layout.use_property_decorate = False

    internal_data = BakeController.get_output_node(settings_bake.internal_name)
    if internal_data is None:
        layout.label(text="Add a Target object and a Map first.", icon="INFO")
    else:
        layout.prop(settings_bake, "use_multires")
        layout.prop(settings_bake, "margin")
        layout.prop(settings_bake, "margin_type")
        layout.prop(settings_bake, "target")
        layout.prop(settings_bake, "use_clear")


class UBK_UL_BakerSettingsBakingPanel(UBK_UL_SettingsPanel, bpy.types.Panel):
    bl_parent_id = "UBK_PT_settings_baker_panel"
    bl_label = "Baking"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        draw_map_settings(self, context, draw_baking_settings)


class UBK_UL_GlobalBakerSettingsBakingPanel(UBK_UL_GlobalSettingsPanel, bpy.types.Panel):
    bl_parent_id = "UBK_PT_global_settings_baker_panel"
    bl_label = "Baking"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        draw_global_output_settings(self, context, draw_baking_settings)


# -------------------------------------------------------------------------
# Sampling Settings Panel
# -------------------------------------------------------------------------


def draw_sampling_settings(layout, settings_bake):
    layout.use_property_split = True
    layout.use_property_decorate = False

    internal_data = BakeController.get_output_node(settings_bake.internal_name)
    if internal_data is None:
        layout.label(text="Add a Target object and a Map first.", icon="INFO")
    else:
        layout.prop(settings_bake, "adaptive_sampling")
        if settings_bake.adaptive_sampling:
            layout.prop(settings_bake, "noise_threshold")
            layout.prop(settings_bake, "min_samples")
            layout.prop(settings_bake, "max_samples")
        else:
            layout.prop(settings_bake, "samples")
        # layout.prop(settings_bake, "denoise")


class UBK_UL_BakerSettingsSamplingPanel(UBK_UL_SettingsPanel, bpy.types.Panel):
    bl_parent_id = "UBK_PT_settings_baker_panel"
    bl_label = "Sampling"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        draw_map_settings(self, context, draw_sampling_settings)


class UBK_UL_GlobalBakerSettingsSamplingPanel(UBK_UL_GlobalSettingsPanel, bpy.types.Panel):
    bl_parent_id = "UBK_PT_global_settings_baker_panel"
    bl_label = "Sampling"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        draw_global_output_settings(self, context, draw_sampling_settings)


classes = (
    UBK_UL_BakerSettingsPanel,
    UBK_UL_GlobalBakerSettingsPanel,
    UBK_UL_BakerSettingsBakingPanel,
    UBK_UL_BakerSettingsSamplingPanel,
    UBK_UL_BakerSettingsOutputPanel,
    UBK_UL_GlobalBakerSettingsBakingPanel,
    UBK_UL_GlobalBakerSettingsSamplingPanel,
    UBK_UL_GlobalBakerSettingsOutputPanel,
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
