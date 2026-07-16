from __future__ import annotations
from typing import Callable

import bpy

from ..core.controller import BakeController

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


def draw_global_settings(self, context, draw: Callable):
    project = BakeController.project(context)
    if project is None:
        return

    layout = self.layout

    settings_pack = project.settings_pack

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
    bl_label = "Packer Settings"

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
        layout.prop(active_packer, "override_settings_pack", toggle=1)
        if active_packer.override_settings_pack:
            box.label(text=f"{active_packer.image_name} settings")
        else:
            box.label(text="Inherited from Global Settings")


# ---------------------------------------------------V----------------------
# Packer output Settings Panel
# -------------------------------------------------------------------------


class UBK_UL_BakeSettingsPanel(UBK_UL_SettingsPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_settings_bake_panel"
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
        layout.prop(active_map, "override_settings_bake", toggle=1)
        if active_map.override_settings_bake:
            box.label(text=f"{active_object.target.name}_{active_map.image_name} settings")
        else:
            box.label(text="Inherited from Global Settings")


classes = (
    UBK_UL_PackerPanel,
    UBK_UL_PackerSettingsPanel,
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
