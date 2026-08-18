from __future__ import annotations

import bpy


PREVIEW_MATERIAL_NAME = "UBK_INTERNAL_PREVIEW"


class PreviewMaterialService:
    @staticmethod
    def get_or_create():

        material = bpy.data.materials.get(PREVIEW_MATERIAL_NAME)

        if material is not None:
            return material

        material = bpy.data.materials.new(PREVIEW_MATERIAL_NAME)
        material.use_nodes = True

        return material

    @staticmethod
    def clear():

        material = bpy.data.materials.get(PREVIEW_MATERIAL_NAME)

        if material is None:
            return

        bpy.data.materials.remove(material)
