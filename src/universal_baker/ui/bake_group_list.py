from __future__ import annotations

import bpy


class UBK_UL_BakeGroupList(bpy.types.UIList):
    """UIList displaying the bake targets."""

    bl_idname = "UBK_UL_BakeGroupList"

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)

        flags = [self.bitflag_filter_item] * len(items)
        order = []

        return flags, order

    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index, flt_flag):
        obj_settings = item

        if self.layout_type in {"DEFAULT", "COMPACT"}:
            self.draw_default(layout, obj_settings, index)

        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"

            layout.label(text="", icon="MESH_CUBE")

    def draw_default(self, layout, active_bake_group, index: int):
        """Draw one object row."""

        row = layout.row(align=True)

        row.prop(active_bake_group, "enabled", text="")
        row.prop(active_bake_group.name)

        enabled_targets = sum(target_object.enabled for target_object in active_bake_group.target_objects)
        total_targets = len(active_bake_group.target_objects)

        enabled_bakers = sum(bake_map.enabled for bake_map in active_bake_group.bakers)
        total_bakers = len(active_bake_group.bakers)

        stats = row.row()
        stats.alignment = "RIGHT"

        stats.enabled = False

        stats.label(text=f"{enabled_targets}/{total_targets}", icon="OBJECT_DATA")
        stats.label(text=f"{enabled_bakers}/{total_bakers}", icon="RENDERLAYERS")

        op = row.operator(
            "ubk.bake_group",
            text="",
            icon="RENDER_STILL",
        )

        op.index = index

    def draw_filter(self, context, layout):
        """Reserved for future filtering options."""
        pass


classes = (UBK_UL_BakeGroupList,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
