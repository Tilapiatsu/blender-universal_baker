from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any

import bpy

from ..core.registry_baker import registry_baker
from ..resources.baker_asset import BakerAsset
from ..runtime.baker_setup import BakerExecution
from ..runtime.context_bake import BakeContext
from ..services.custom_baker_setup import CustomBakerSetupService
from .base import BakerBase

if TYPE_CHECKING:
    from ..parameter.metadata import ParameterMetadata


class CustomBaker(BakerBase):
    """Custom bake defined in an external blend file."""

    id = "CUSTOM"
    name = "Custom"
    description = "Custom bake defined in an external blend file."
    icon = "TEXTURE"
    blender_bake_type = "EMIT"
    accumulator_id = "ALPHA_OVER"
    asset_path: Path
    is_custom: bool = True

    @property
    def parameters(self) -> tuple[ParameterMetadata, ...]:
        return super().parameters

    @contextmanager
    def prepare_execution(self, target: bpy.types.Object) -> Generator[BakerExecution, Any, Any]:
        asset = BakerAsset(filepath=self.asset_path)

        hide_render = target.hide_render
        setup = CustomBakerSetupService.prepare(asset=asset, target=target)

        try:
            yield BakerExecution(target=setup.target, setup=setup)

        finally:
            target.hide_render = hide_render
            setup.cleanup()

    def execute(self, ctx: BakeContext) -> None:
        return super().execute(ctx)

    def configure_preview_material(self, material):
        asset = BakerAsset(filepath=self.asset_path)
        material.use_nodes = True
        dst_tree = material.node_tree
        dst_tree.nodes.clear()

        src_tree = CustomBakerSetupService.get_prototype_material(asset).node_tree
        node_mapping = {}

        for node in src_tree.nodes:
            new_node = dst_tree.nodes.new(type=node.bl_idname)
            new_node.location = node.location
            new_node.width = node.width
            new_node.name = node.name

            for i, input_sock in enumerate(node.inputs):
                if i < len(new_node.inputs) and not input_sock.is_linked:
                    try:
                        new_node.inputs[i].default_value = input_sock.default_value
                    except AttributeError:
                        pass

            if hasattr(node, "image") and hasattr(new_node, "image"):
                new_node.image = node.image

            if hasattr(node, "node_tree"):
                new_node.node_tree = node.node_tree

            node_mapping[node] = new_node

        for link in src_tree.links:
            from_node = node_mapping.get(link.from_node)
            to_node = node_mapping.get(link.to_node)

            if from_node and to_node:
                from_sock_idx = list(link.from_node.outputs).index(link.from_socket)
                to_sock_idx = list(link.to_node.inputs).index(link.to_socket)

                if not len(from_node.outputs) or not len(to_node.inputs):
                    continue

                dst_tree.links.new(from_node.outputs[from_sock_idx], to_node.inputs[to_sock_idx])

    def prepare(self, ctx: BakeContext):
        """
        Prepare everything required before Blender's bake.
        """
        super().prepare(ctx)
        self.apply_parameters(ctx)

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


classes = (CustomBaker,)


def register():
    for c in classes:
        baker = c()
        baker.register_custom()


def unregister():
    for c in classes:
        registry_baker.unregister_custom(c.id)


def refresh():
    unregister()
    register()
