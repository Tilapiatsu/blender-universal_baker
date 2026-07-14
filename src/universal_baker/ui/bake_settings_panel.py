from __future__ import annotations

import bpy

from ..services.project import ProjectService
from ..services.map import MapService


class UBK_UL_BakeSettingsOutputPanel(bpy.types.Panel):
    """Output Baker panel."""

    bl_idname = "UBK_PT_bake_output_panel"
    bl_label = "Output"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Universal Baker"

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Output")

    def draw(self, context):
        layout = self.layout
        project = ProjectService.get(context)
        if project is None:
            return

        active_map = MapService.active(project)

        if active_map is None:
            return

        bake_settings = active_map.bake_settings

        layout.prop(bake_settings, "resolution_x")
        layout.prop(bake_settings, "resolution_y")


classes = (UBK_UL_BakeSettingsOutputPanel,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
