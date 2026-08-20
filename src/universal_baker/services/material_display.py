from __future__ import annotations

import bpy


DISPLAY_MATERIAL_NAME = "UBK_INTERNAL_BAKE_DISPLAY"


class DisplayMaterialService:
    @staticmethod
    def get_or_create():
        material = bpy.data.materials.get(DISPLAY_MATERIAL_NAME)

        if material is None:
            material = bpy.data.materials.new(DISPLAY_MATERIAL_NAME)

            material.use_nodes = True

        return material

    @staticmethod
    def set_image(material: bpy.types.Material, image: bpy.types.Image):
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        nodes.clear()
        output = nodes.new("ShaderNodeOutputMaterial")
        shader = nodes.new("ShaderNodeBsdfPrincipled")
        texture = nodes.new("ShaderNodeTexImage")
        texture.image = image

        links.new(
            texture.outputs["Color"],
            shader.inputs["Base Color"],
        )

        links.new(
            shader.outputs["BSDF"],
            output.inputs["Surface"],
        )
