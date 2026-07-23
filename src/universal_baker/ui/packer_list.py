from __future__ import annotations

import bpy

# from ..core.registry_baker import registry_baker


class UBK_UL_PackList(bpy.types.UIList):
    """UIList displaying the packer items."""

    bl_idname = "UBK_UL_PackList"

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)

        flags = [self.bitflag_filter_item] * len(items)
        order = []

        return flags, order

    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index, flt_flag):
        pack_item = item

        if self.layout_type in {"DEFAULT", "COMPACT"}:
            self.draw_default(layout, pack_item, index)

        elif self.layout_type == {"GRID"}:
            layout.alignment = "CENTER"
            layout.label(icon="TEXTURE")

    def draw_default(self, layout, pack_item, index: int):
        row = layout.row(align=True)

        row.prop(pack_item, "enabled", text="")

        row.label(text=pack_item.image_name, icon="NODE_COMPOSITING")

        info = row.row()
        info.alignment = "RIGHT"
        info.enabled = False

        if pack_item.override_settings:
            resolution = f"{pack_item.settings.width}×{pack_item.settings.height}"

            info.label(text=resolution, icon="IMAGE_DATA")

        else:
            info.label(text="Global", icon="SETTINGS")

        # --------------------------------------------------------------
        # TODO : add preview operator ?
        # --------------------------------------------------------------
        # preview = row.operator(
        #     "ubk.preview_map",
        #     text="",
        #     icon='HIDE_OFF',
        # )
        #
        # preview.index = index
        #

        pack = row.operator(
            "ubk.pack_selected",
            text="",
            icon="NODE_COMPOSITING",
        )

        pack.index = index

    def draw_filter(self, context, layout):
        """Reserved for future filtering."""
        pass


classes = (UBK_UL_PackList,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
