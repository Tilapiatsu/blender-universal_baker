from __future__ import annotations

import bpy

from ..core.controller import BakeController


class UBK_PT_MainPanel(bpy.types.Panel):
    """Main Universal Baker panel."""

    bl_idname = "UBK_PT_main_panel"
    bl_label = "Universal Baker"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Universal Baker"

    def draw(self, context):
        layout = self.layout
        project = BakeController.project(context)

        self.draw_header(context)
        self.draw_objects(layout, context, project)
        self.draw_maps(layout, context, project)
        self.draw_footer(layout, context, project)

    def draw_header(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.label(text="Bake Project", icon="RENDER_STILL")

    def draw_objects(self, layout, context, project):
        box = layout.box()
        header = box.row()
        header.label(text="Target Objects", icon="OUTLINER_OB_MESH")
        box.template_list("UBK_UL_ObjectList", "", project, "objects", project, "active_object_index", rows=5)
        row = box.row(align=True)
        row.operator("ubk.add_object", text="Add Selected", icon="ADD")
        row.operator("ubk.remove_object", text="", icon="REMOVE")

    def draw_maps(self, layout, context, project):
        box = layout.box()
        header = box.row()
        header.label(text="Bake Maps", icon="TEXTURE")
        active_object = BakeController.active_object(context)

        if active_object is None:
            box.label(text="Select a target object.", icon="INFO")

            return

        box.template_list("UBK_UL_BakerList", "", active_object, "maps", active_object, "active_map_index", rows=5)

        row = box.row(align=True)
        row.operator("ubk.add_map", text="Add Map", icon="ADD")
        row.operator("ubk.remove_map", text="", icon="REMOVE")

    def draw_footer(self, layout, context, project):
        layout.separator()
        row = layout.row()
        row.scale_y = 1.6
        row.operator("ubk.bake_all", icon="RENDER_STILL")


classes = (UBK_PT_MainPanel,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
