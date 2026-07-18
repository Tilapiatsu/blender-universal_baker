from __future__ import annotations

import bpy

from ..core.controller import BakeController

# -------------------------------------------------------------------------
# Decorators
# -------------------------------------------------------------------------


def object_needed(func):
    def wrapper(self, context):
        project = BakeController.project(context)
        if project is None:
            return

        active_object = BakeController.active_object(context)

        if active_object is None:
            layout = self.layout
            box = layout.box()
            header = box.row()
            header.label(text="Add a Target Object.", icon="INFO")
            return

        func(self, context)

    return wrapper


def baker_needed(func):
    def wrapper(self, context):
        project = BakeController.project(context)
        if project is None:
            return

        active_object = BakeController.active_object(context)

        if active_object is None:
            layout = self.layout
            box = layout.box()
            header = box.row()
            header.label(text="Add a Target Object.", icon="INFO")
            return

        active_baker = BakeController.active_baker(context)

        if active_baker is None:
            layout = self.layout
            box = layout.box()
            header = box.row()
            header.label(text="Add a Baker.", icon="INFO")
            return

        func(self, context)

    return wrapper


def packer_needed(func):
    def wrapper(self, context):
        project = BakeController.project(context)
        if project is None:
            return

        active_object = BakeController.active_object(context)

        if active_object is None:
            layout = self.layout
            box = layout.box()
            header = box.row()
            header.label(text="Add a Target Object.", icon="INFO")
            return

        active_packer = BakeController.active_packer(context)

        if active_packer is None:
            layout = self.layout
            box = layout.box()
            header = box.row()
            header.label(text="Add a Packer.", icon="INFO")
            return

        func(self, context)

    return wrapper


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


# -------------------------------------------------------------------------
# Main Panel
# -------------------------------------------------------------------------


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
        self.draw_objects(context, project)
        self.draw_maps(context)
        self.draw_settings(context)
        self.draw_footer(context)

    def draw_header(self, context):
        layout = self.layout
        # box = layout.box()
        # row = box.row()
        # row.label(text="Bake Project", icon="RENDER_STILL")

    def draw_objects(self, context, project):
        box = self.layout.box()
        header = box.row()
        header.label(text="Target Objects", icon="OUTLINER_OB_MESH")
        box.template_list("UBK_UL_ObjectList", "", project, "objects", project, "active_object_index", rows=5)
        row = box.row(align=True)
        row.operator("ubk.add_object", text="Add Selected", icon="ADD")
        row.operator("ubk.remove_object", text="", icon="REMOVE")

    @object_needed
    def draw_maps(self, context):
        box = self.layout.box()
        header = box.row()
        header.label(text="Baker", icon="TEXTURE")
        active_object = BakeController.active_object(context)

        box.template_list("UBK_UL_BakerList", "", active_object, "maps", active_object, "active_baker_index", rows=5)

        row = box.row(align=True)
        row.operator("ubk.add_baker", icon="ADD")
        row.operator("ubk.remove_baker", text="", icon="REMOVE")

    @baker_needed
    def draw_settings(self, context):
        pass
        # self.layout.panel("UBK_PT_settings_baker_panel", default_closed=True)

    def draw_footer(self, context):
        self.layout.separator()
        row = self.layout.row()
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
