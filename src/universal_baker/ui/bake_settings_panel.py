from __future__ import annotations

import bpy

from ..services.object import ObjectService
from ..services.project import ProjectService
from ..services.map import MapService
from ..services.internal_data import InternalDataService


class UBK_UL_SettingsPanel:
    """Bake Settings panel."""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Universal Baker"


class UBK_UL_BakeSettingsPanel(UBK_UL_SettingsPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_bake_settings_panel"
    bl_label = "Map Bake Settings"

    def draw(self, context):
        project = ProjectService.get(context)
        if project is None:
            return

        layout = self.layout
        box = layout.box()
        header = box.row()

        active_object = ObjectService.active(project)
        if active_object is None:
            header.label(text="Add a target Object.", icon="INFO")
            return

        active_map = MapService.active(project)
        if active_map is None:
            header.label(text="Add a Bake Map.", icon="INFO")
            return

        box.prop(active_map, "image_name")
        box.prop(active_map, "override_bake_settings")
        if active_map.override_bake_settings:
            box.label(text=f"{active_object.target.name}_{active_map.image_name} settings")
        else:
            box.label(text="Inherited from Global Settings")


def draw_bake_settings(layout, bake_settings):
    internal_data = InternalDataService.get_output_node(bake_settings.internal_name)
    if internal_data is None:
        layout.label(text="Add a Target object and a Map first.", icon="INFO")
    else:
        layout.prop(bake_settings, "resolution_x")
        layout.prop(bake_settings, "resolution_y")
        layout.template_image_settings(internal_data.format, color_management=False)


class UBK_UL_BakeSettingsOutputPanel(UBK_UL_SettingsPanel, bpy.types.Panel):
    bl_parent_id = "UBK_PT_bake_settings_panel"
    bl_label = "Output"

    def draw(self, context):
        project = ProjectService.get(context)
        if project is None:
            return

        active_map = MapService.active(project)
        if active_map is None:
            return

        layout = self.layout

        if active_map.override_bake_settings:
            bake_settings = active_map.bake_settings
        else:
            bake_settings = project.bake_settings
            layout.enabled = False

        draw_bake_settings(layout, bake_settings)


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


class UBK_UL_GlobalBakeSettingsOutputPanel(UBK_UL_GlobalSettingsPanel, bpy.types.Panel):
    bl_parent_id = "UBK_PT_global_bake_settings_panel"
    bl_label = "Output"

    def draw(self, context):
        project = ProjectService.get(context)
        if project is None:
            return

        layout = self.layout

        bake_settings = project.bake_settings

        draw_bake_settings(layout, bake_settings)


classes = (
    UBK_UL_BakeSettingsPanel,
    UBK_UL_BakeSettingsOutputPanel,
    UBK_UL_GlobalBakeSettingsPanel,
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
