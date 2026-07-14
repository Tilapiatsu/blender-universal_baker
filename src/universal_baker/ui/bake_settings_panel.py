from __future__ import annotations

import bpy
from universal_baker.services.object import ObjectService

from ..services.project import ProjectService
from ..services.map import MapService


class UBK_UL_BakeSettingsPanel(bpy.types.Panel):
    """Bake Settings panel."""

    bl_idname = "UBK_PT_bake_settings_panel"
    bl_label = "Bake Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Universal Baker"

    def draw(self, context):
        project = ProjectService.get(context)
        if project is None:
            return

        active_object = ObjectService.active(project)
        if active_object is None:
            return

        active_map = MapService.active(project)
        if active_map is None:
            return

        layout = self.layout
        box = layout.box()
        header = box.row()
        if active_map is None:
            header.label(text="Select a map.", icon="INFO")

            return

        header.label(text=f"{active_object.target.name} | {active_map.image_name} settings")


class UBK_UL_BakeSettingsOutputPanel(UBK_UL_BakeSettingsPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_bake_settings_output_panel"
    bl_label = "Output"
    bl_parent_id = "UBK_PT_bake_settings_panel"

    def draw(self, context):
        project = ProjectService.get(context)
        if project is None:
            return

        active_map = MapService.active(project)
        if active_map is None:
            return

        layout = self.layout
        bake_settings = active_map.bake_settings

        layout.prop(bake_settings, "resolution_x")
        layout.prop(bake_settings, "resolution_y")


classes = (
    UBK_UL_BakeSettingsPanel,
    UBK_UL_BakeSettingsOutputPanel,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
