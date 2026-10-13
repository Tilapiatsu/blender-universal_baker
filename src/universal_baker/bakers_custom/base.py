from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any

from universal_baker.constant import LOG

from ..bakers.base import BakerBase
from ..core.registry_baker import registry_baker
from ..core.registry_definition import registry_definition
from ..parameter.baker_custom.metadata_loader import MetadataLoader as metadata_loader_custom
from ..resources.asset_external import AssetExtrenal
from ..runtime.asset_setup import BakerExecution
from ..runtime.bake_objects import BakeObjects
from ..runtime.context_bake import BakeContext
from ..services.asset_external_setup import AssetExternalBakeSetup
from ..services.visibility_override import VisibilityOverride

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
    is_custom: bool = True

    @property
    def asset_path(self) -> Path | None:
        assets_path = Path(__file__).parent / "assets"
        blend_files = [
            f
            for f in assets_path.iterdir()
            if f.is_file() and f.suffix.lower() == ".blend" and f.stem == self.id.lower()
        ]

        if len(blend_files) == 0 or len(blend_files) > 1:
            LOG.error(f"{len(blend_files)} .blend files found while registering Custom Baker")
            for f in blend_files:
                LOG.debug(f.name)
            return

        return blend_files[0]

    @property
    def parameters(self) -> tuple[ParameterMetadata, ...]:
        return super().parameters

    @contextmanager
    def prepare_execution(
        self,
        bake_objects: BakeObjects,
    ) -> Generator[BakerExecution, Any, Any]:
        assert self.asset_path is not None
        asset = AssetExtrenal(filepath=self.asset_path)

        hide_render = {}

        for s in bake_objects.baker_material_objects:
            hide_render[s] = s.hide_render

        setup = AssetExternalBakeSetup.prepare(
            asset=asset,
            bake_objects=bake_objects,
        )

        try:
            yield BakerExecution(
                target=setup.target,
                cage=setup.cage,
                sources=setup.sources,
                setup=setup,
            )

        finally:
            for obj, render in hide_render.items():
                obj.hide_render = render
            setup.cleanup()

    def execute(self, ctx: BakeContext) -> None:
        return super().execute(ctx)

    def invalidate_previous_output(self, ctx: BakeContext) -> None:
        super().invalidate_previous_output(ctx)

    def configure_preview_material(self, material):
        assert self.asset_path is not None
        asset = AssetExtrenal(filepath=self.asset_path)
        material.use_nodes = True
        dst_tree = material.node_tree
        dst_tree.nodes.clear()

        with AssetExternalBakeSetup.get_prototype_material(asset) as prototype_material:
            src_tree = prototype_material.node_tree
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

    def get_visibility_overrides(self, ctx: BakeContext) -> list[VisibilityOverride]:
        """Set Visibility."""
        l: list[VisibilityOverride] = []
        return l

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

    def register_custom(self):
        if self.asset_path is None:
            return

        LOG.info(f"Registering Building Custom Baker : {self.id}")
        self.register_property_class()
        registry_baker.register(self)

        registry_definition.register_custom_lazy(
            identifier=self.id,
            asset_path=self.asset_path,
            loader=metadata_loader_custom.load_definition,
        )
