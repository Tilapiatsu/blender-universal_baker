from __future__ import annotations

import bpy

from ..constant import ICON_BAKE, ICON_SOURCE_OBJECT, ICON_TARGET_OBJECT
from .list import draw_indent, draw_source_objects


class UBK_UL_TargetObjectList(bpy.types.UIList):
    """UIList displaying the bake target objects."""

    bl_idname = "UBK_UL_TargetObjectList"

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)

        flags = [self.bitflag_filter_item] * len(items)
        order = []

        return flags, order

    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index, flt_flag):
        obj_settings = item

        if self.layout_type in {"DEFAULT", "COMPACT"}:
            self.draw_default(layout, obj_settings, 0, index)

        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"

            layout.label(text="", icon=ICON_TARGET_OBJECT)

    def draw_default(self, layout, item, indent: int, index: int):
        """Draw one object row."""

        column = layout.column(align=True)
        row = column.row(align=True)

        if len(item.source_objects) > 0:
            draw_indent(item, row, "expanded_target", indent)

        row.prop(item, "enabled", text="")

        row = row.row(align=True)
        if not item.enabled:
            row.enabled = False

        obj = item.object

        if obj is not None:
            row.prop(obj, "name", text="", emboss=False, icon=ICON_TARGET_OBJECT)

        else:
            row.label(text="<Missing Object>", icon="ERROR")

        source_objects = len([o for o in item.source_objects if o.enabled])

        stats = row.row()

        stats.enabled = False
        stats.alignment = "RIGHT"

        if source_objects:
            stats.label(text=f"{source_objects}", icon=ICON_SOURCE_OBJECT)
        else:
            stats.label(text="no source")

        row.operator("ubk.bake_target", text="", icon=ICON_BAKE).index = index

        if item.expanded_target:
            draw_source_objects(column, item, indent + 1)

    def draw_filter(self, context, layout):
        """Reserved for future filtering options."""
        pass


classes = (UBK_UL_TargetObjectList,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
