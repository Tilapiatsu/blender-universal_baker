from __future__ import annotations

import bpy

from ..core.registry_baker import registry_baker


class UBK_UL_BakerList(bpy.types.UIList):
    """UIList displaying the bake maps of the active object."""

    bl_idname = "UBK_UL_BakerList"

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

    def draw_default(self, layout, bake_map, index: int):
        row = layout.row(align=True)

        row.prop(bake_map, "enabled", text="")
        baker = None

        if registry_baker.exists(bake_map.baker):
            baker = registry_baker[bake_map.baker]

        if baker:
            row.label(text=baker.name, icon=baker.icon)

        else:
            row.label(text=bake_map.baker, icon="QUESTION")

        info = row.row()
        info.alignment = "RIGHT"
        info.enabled = False

        if bake_map.override_settings:
            resolution = f"{bake_map.settings.resolution_x}×{bake_map.settings.resolution_y}"

            info.label(text=resolution, icon="IMAGE_DATA")

        else:
            info.label(text="Global", icon="SETTINGS")

        # --------------------------------------------------------------
        # Future Preview
        # --------------------------------------------------------------

        #
        # preview = row.operator(
        #     "ubk.preview_map",
        #     text="",
        #     icon='HIDE_OFF',
        # )
        #
        # preview.index = index
        #

        bake = row.operator(
            "ubk.bake_map",
            text="",
            icon="RENDER_STILL",
        )

        bake.index = index

    def draw_filter(self, context, layout):
        """Reserved for future filtering."""
        pass


classes = (UBK_UL_BakerList,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
