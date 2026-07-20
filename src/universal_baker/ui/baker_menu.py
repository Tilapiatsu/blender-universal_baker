from __future__ import annotations

import bpy

from ..core.registry_baker import registry_baker


class UBK_MT_BakerAddMenu(bpy.types.Menu):
    bl_idname = "UBK_MT_BakerAddMenu"
    bl_label = "Add Baker"

    def draw(self, context):
        layout = self.layout

        for b in registry_baker.keys():
            layout.operator("ubk.add_baker", text=b).baker_id = registry_baker[b].id


classes = (UBK_MT_BakerAddMenu,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
