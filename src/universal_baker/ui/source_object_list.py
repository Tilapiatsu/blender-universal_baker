from __future__ import annotations

import bpy


class UBK_UL_SourceObjectList(bpy.types.UIList):
    """UIList displaying the bake source objects."""

    bl_idname = "UBK_UL_SourceObjectList"

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

    def draw_default(self, layout, obj_settings, index: int):
        """Draw one object row."""

        row = layout.row(align=True)

        row.prop(obj_settings, "enabled", text="")

        obj = obj_settings.object

        if obj is not None:
            row.prop(obj, "name", text="", emboss=False, icon="MESH_UVSPHERE")

        else:
            row.label(text="<Missing Object>", icon="ERROR")

    def draw_filter(self, context, layout):
        """Reserved for future filtering options."""
        pass


classes = (UBK_UL_SourceObjectList,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
