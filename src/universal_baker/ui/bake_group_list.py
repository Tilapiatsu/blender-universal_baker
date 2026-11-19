from __future__ import annotations

import bpy

from ..constant import ICON_BAKE, ICON_TARGET_OBJECT
from .list import draw_indent, draw_target_objects


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
            self.draw_bake_group(layout, obj_settings, 0, index)

        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"

            layout.label(text="", icon=ICON_TARGET_OBJECT)

    def draw_bake_group(self, layout, item, indent: int, index: int):
        """Draw one object row."""
        column = layout.column(align=True)
        row = column.row(align=True)

        draw_indent(item, row, "expanded", indent, len(item.target_objects))

        row.prop(item, "enabled", text="")

        row = row.row(align=True)
        if not item.enabled:
            row.enabled = False

        row.prop(item, "name", placeholder="Name", emboss=False, text="")

        enabled_targets = sum(target_object.enabled for target_object in item.target_objects)
        total_targets = len(item.target_objects)

        enabled_bakers = sum(baker.enabled for baker in item.bakers)
        total_bakers = len(item.bakers)

        stats = row.row()
        stats.alignment = "RIGHT"

        stats.enabled = False

        stats.label(text=f"{enabled_targets}/{total_targets}", icon=ICON_TARGET_OBJECT)
        stats.label(text=f"{enabled_bakers}/{total_bakers}", icon="RENDERLAYERS")

        row = row.row(align=True)
        row.alignment = "RIGHT"
        row.prop(
            item,
            "detect_udim",
            text="UDIM",
            icon="VIEW_ORTHO" if item.detect_udim else "MESH_PLANE",
            toggle=True,
        )
        row = row.row(align=True)

        op = row.operator(
            "ubk.bake_group",
            text="",
            icon=ICON_BAKE,
        )

        op.index = index

        if item.expanded:
            draw_target_objects(column, item, "expanded_bake_group", indent + 1, len(item.target_objects))

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
