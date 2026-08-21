from __future__ import annotations

import bpy


class UBK_UL_BakerLibraryList(bpy.types.UIList):
    """UIList displaying the baker libraries available in the preferences."""

    bl_idname = "UBK_UL_BakerLibraryList"

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)

        flags = [self.bitflag_filter_item] * len(items)
        order = []

        return flags, order

    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index, flt_flag):
        bake_map = item

        if self.layout_type in {"DEFAULT", "COMPACT"}:
            self.draw_default(layout, bake_map, index)

        elif self.layout_type == {"GRID"}:
            layout.alignment = "CENTER"
            layout.label(icon="TEXTURE")

    def draw_default(self, layout, item, index: int):
        row = layout.row()
        row.alignment = "LEFT"

        if not item.builtin:
            row.prop(item, "enabled", text="")
        else:
            row.separator()
            row.separator()
            row.separator()
            row.separator()

        row = layout.row()
        row.label(text=item.name, icon="PACKAGE" if item.builtin else "DOCUMENTS")

        row = layout.row()
        row.alignment = "RIGHT"
        row.enabled = False
        row.label(text="Builtin" if item.builtin else "       ")

    def draw_filter(self, context, layout):
        """Reserved for future filtering."""
        pass


classes = (UBK_UL_BakerLibraryList,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
