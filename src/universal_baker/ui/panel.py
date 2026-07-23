from __future__ import annotations

import bpy

from ..core.controller import BakeController


# -------------------------------------------------------------------------
# Decorators
# -------------------------------------------------------------------------
#
def bake_group_needed(func):
    def wrapper(self, context):
        project = BakeController.project(context)
        if project is None:
            return

        active_bake_group = BakeController.active_bake_group(context)

        if active_bake_group is None:
            layout = self.layout
            box = layout.box()
            header = box.row()
            header.label(text="Add a Bake Group.", icon="INFO")
            return

        func(self, context)

    return wrapper


def object_needed(func):
    def wrapper(self, context):
        project = BakeController.project(context)
        if project is None:
            return

        active_bake_group = BakeController.active_bake_group(context)

        if active_bake_group is None:
            layout = self.layout
            box = layout.box()
            header = box.row()
            header.label(text="Add a Bake Group.", icon="INFO")

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

        active_bake_group = BakeController.active_bake_group(context)

        if active_bake_group is None:
            layout = self.layout
            box = layout.box()
            header = box.row()
            header.label(text="Add a Bake Group.", icon="INFO")

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

        active_bake_group = BakeController.active_bake_group(context)

        if active_bake_group is None:
            layout = self.layout
            box = layout.box()
            header = box.row()
            header.label(text="Add a Bake Group.", icon="INFO")

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


def draw_baker_settings(self, layout, context):
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


class UBK_PT_MainPanel:
    """Main Universal Baker panel."""

    bl_label = "Universal Baker"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Universal Baker"


class UBK_PT_UniversalBakerPanel(UBK_PT_MainPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_UniversalBakerPanel"
    bl_label = "Universal Baker"

    def draw(self, context):
        pass


class UBK_PT_BakeGroupPanel(UBK_PT_MainPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_BakeGroupPanel"
    bl_label = ""
    bl_parent_id = "UBK_PT_UniversalBakerPanel"

    def draw(self, context):
        layout = self.layout
        project = BakeController.project(context)

        self.draw_bake_groups(context, project)

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Bake Groups", icon="OUTLINER")

    def draw_bake_groups(self, context, project):
        box = self.layout.box()
        box.template_list(
            "UBK_UL_BakeGroupList", "", project, "bake_groups", project, "active_bake_group_index", rows=5
        )
        row = box.row(align=True)
        row.operator("ubk.add_bake_group", text="Add group", icon="ADD")
        row.operator("ubk.remove_bake_group", text="", icon="REMOVE")


class UBK_PT_ObjectPanel(UBK_PT_MainPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_ObjectPanel"
    bl_label = ""
    bl_parent_id = "UBK_PT_UniversalBakerPanel"

    def draw(self, context):
        layout = self.layout
        project = BakeController.project(context)

        self.draw_objects(context)

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Target Objects", icon="OUTLINER_OB_MESH")

    @bake_group_needed
    def draw_objects(self, context):
        box = self.layout.box()
        active_bake_group = BakeController.active_bake_group(context)

        if active_bake_group is None:
            return

        box.template_list(
            "UBK_UL_ObjectList",
            "",
            active_bake_group,
            "target_objects",
            active_bake_group,
            "active_target_object_index",
            rows=5,
        )
        row = box.row(align=True)
        row.operator("ubk.add_object", text="Add Selected", icon="ADD")
        row.operator("ubk.remove_object", text="", icon="REMOVE")


class UBK_PT_BakerPanel(UBK_PT_MainPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_BakerPanel"
    bl_label = ""
    bl_parent_id = "UBK_PT_UniversalBakerPanel"

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Bakers", icon="TEXTURE")

    def draw(self, context):
        self.draw_bakers(context)

    @bake_group_needed
    def draw_bakers(self, context):
        box = self.layout.box()
        active_bake_group = BakeController.active_bake_group(context)

        box.template_list(
            "UBK_UL_BakerList", "", active_bake_group, "bakers", active_bake_group, "active_baker_index", rows=5
        )

        row = box.row(align=True)
        row.menu("UBK_MT_BakerAddMenu", icon="ADD")
        row.operator("ubk.remove_baker", text="", icon="REMOVE")


class UBK_PT_ProcessPanel(UBK_PT_MainPanel, bpy.types.Panel):
    bl_idname = "UBK_PT_ProcessPanel"
    bl_label = ""
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Universal Baker"

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Process", icon="SETTINGS")

    @bake_group_needed
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.scale_y = 1.6
        col.operator("ubk.bake_all", icon="RENDER_STILL")
        col.operator("ubk.pack_all", icon="NODE_COMPOSITING")
        col.operator("ubk.bake_and_pack_all", icon="LONGDISPLAY")


classes = (
    UBK_PT_UniversalBakerPanel,
    UBK_PT_BakeGroupPanel,
    UBK_PT_ObjectPanel,
    UBK_PT_BakerPanel,
    UBK_PT_ProcessPanel,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
