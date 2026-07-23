from __future__ import annotations
from typing import Callable

import bpy

from ..core.controller import BakeController
from .panel_settings_output import (
    draw_output_settings,
)
from .panel import (
    baker_needed,
    draw_sampling_settings,
    draw_baking_settings,
    UBK_PT_MainPanel,
)


def draw_map_settings(self, context, draw: Callable):
    project = BakeController.project(context)
    if project is None:
        return

    active_baker = BakeController.active_baker(context)
    if active_baker is None:
        return

    layout = self.layout

    if active_baker.override_settings:
        settings_bake = active_baker.settings
    else:
        settings_bake = project.settings_bake
        layout.enabled = False

    draw(layout, settings_bake)


# -------------------------------------------------------------------------
# Main Settings Panel
# -------------------------------------------------------------------------


class UBK_PT_BakerSettingsPanel(UBK_PT_MainPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_settings_baker_panel"
    bl_label = ""
    bl_parent_id = "UBK_PT_BakerPanel"

    @classmethod
    def poll(cls, context):
        return BakeController.active_baker(context) is not None

    def draw_header(self, context):
        layout = self.layout
        active_baker = BakeController.active_baker(context)
        if active_baker is None:
            layout.label(text="Baker Settings", icon="TEXTURE")
            return

        layout.label(text=f"{active_baker.baker.capitalize()} Settings", icon="TEXTURE")

    @baker_needed
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.use_property_split = True
        box.use_property_decorate = False

        active_bake_group = BakeController.active_bake_group(context)
        if active_bake_group is None:
            return

        active_baker = BakeController.active_baker(context)
        if active_baker is None:
            return

        box.prop(active_baker, "image_name")
        layout.prop(active_baker, "override_settings", toggle=1)
        if active_baker.override_settings:
            box.label(text=f"{active_baker.image_name} settings")
        else:
            box.label(text="Inherited from Global Settings")


# -------------------------------------------------------------------------
# Output Settings Panel
# -------------------------------------------------------------------------


class UBK_PT_BakerSettingsOutputPanel(UBK_PT_MainPanel, bpy.types.Panel):
    bl_parent_id = "UBK_PT_settings_baker_panel"
    bl_label = "Output"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        draw_map_settings(self, context, draw_output_settings)


# -------------------------------------------------------------------------
# Bake Settings Panel
# -------------------------------------------------------------------------


class UBK_PT_BakerSettingsBakingPanel(UBK_PT_MainPanel, bpy.types.Panel):
    bl_parent_id = "UBK_PT_settings_baker_panel"
    bl_label = "Baking"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        draw_map_settings(self, context, draw_baking_settings)


# -------------------------------------------------------------------------
# Sampling Settings Panel
# -------------------------------------------------------------------------


class UBK_PT_BakerSettingsSamplingPanel(UBK_PT_MainPanel, bpy.types.Panel):
    bl_parent_id = "UBK_PT_settings_baker_panel"
    bl_label = "Sampling"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        draw_map_settings(self, context, draw_sampling_settings)


classes = (
    UBK_PT_BakerSettingsPanel,
    UBK_PT_BakerSettingsBakingPanel,
    UBK_PT_BakerSettingsSamplingPanel,
    UBK_PT_BakerSettingsOutputPanel,
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
