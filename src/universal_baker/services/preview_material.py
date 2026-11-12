from __future__ import annotations

import bpy

from ..services.data_removal import MaterialRemoval

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

        MaterialRemoval.remove_material(material)

    def __enter__(self):
        return self.get_or_create()

    def __exit__(self, exc_type, exc_value, traceback):
        self.clear()
