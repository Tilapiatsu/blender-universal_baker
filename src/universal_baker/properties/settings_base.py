from __future__ import annotations

import bpy

from bpy.types import PropertyGroup
from ..services.internal_data import InternalDataService


class UBK_Settings(PropertyGroup):
    internal_name: bpy.props.StringProperty(default="Default")

    @property
    def file_format_settings(self):
        node = InternalDataService.get_output_node(self.internal_name)
        if node is None:
            return

        return node.format


def get_colorspace_items(self, context):
    items = [("Non-Color", "Non-Color", "")]
    for i in bpy.types.Image.bl_rna.properties["colorspace_settings"].fixed_type.properties["name"].enum_items:
        if (i.name, i.name, "") in items:
            continue
        items.append((i.name, i.name, ""))
    return items
