from __future__ import annotations

import bpy

from .base import BakerBase

from ..runtime.context_bake import BakeContext
from ..core.registry_baker import registry_baker


class AmbientOcclusionBaker(BakerBase):
    """Bake the diffuse/albedo color."""

    id = "AO"
    name = "Ambient Occlusion"
    description = "Bake Ambient Occlusion"
    icon = "TEXTURE"
    blender_bake_type = "AO"
    accumulator_id = "ALPHA_OVER"

    def execute(self, ctx: BakeContext) -> None:
        return super().execute(ctx)

    def prepare_execution(self, target: bpy.types.Object):
        return super().prepare_execution(target)

    def configure_preview_material(self, material):
        # TODO: Need to expose the AO Parameters
        material.use_nodes = True
        nodes = material.node_tree.nodes
        nodes.clear()

        output = nodes.new("ShaderNodeOutputMaterial")
        shader = nodes.new("ShaderNodeAmbientOcclusion")

        material.node_tree.links.new(
            shader.outputs["Color"],
            output.inputs["Surface"],
        )

    def prepare(self, ctx: BakeContext):
        """
        Prepare everything required before Blender's bake.
        """
        super().prepare(ctx)

    def bake(self, ctx: BakeContext) -> None:
        """Execute the bake."""
        return super().bake(ctx)

    def cleanup(self, ctx: BakeContext):
        """
        Cleanup after baking.
        """
        super().cleanup(ctx)

    def update_baker(self, ctx: BakeContext) -> None:
        return super().update_baker(ctx)

    def create_artifact(self, ctx: BakeContext) -> None:
        return super().create_artifact(ctx)

    def export_file(self, ctx: BakeContext):
        """Save Bake to disk."""
        super().export_file(ctx)


classes = (AmbientOcclusionBaker,)


def register():
    for c in classes:
        registry_baker.register(c())


def unregister():
    pass
