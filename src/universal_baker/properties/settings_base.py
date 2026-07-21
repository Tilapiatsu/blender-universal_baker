from __future__ import annotations

import bpy

from bpy.types import PropertyGroup


class UBK_Settings(PropertyGroup):
    internal_name: bpy.props.StringProperty(default="Default")


def get_colorspace_items(self, context):
    items = [("Non-Color", "Non-Color", "")]
    for i in bpy.types.Image.bl_rna.properties["colorspace_settings"].fixed_type.properties["name"].enum_items:
        if (i.name, i.name, "") in items:
            continue
        items.append((i.name, i.name, ""))
    return items
