from __future__ import annotations

from contextlib import contextmanager
from dataclasses import field
from pathlib import Path
from typing import Any, Generator
import bpy

from ..custom_bakers.parameter_applier import ParameterApplier
from ..custom_bakers.metadata_loader import MetadataLoader
from ..core.registry_definition import registry_definition

from ..parameter.parameter_context import ParameterContext

from .base import BakerBase

from ..runtime.baker_setup import BakerExecution
from ..runtime.context_bake import BakeContext
from ..core.registry_baker import registry_baker
from ..resources.baker_asset import BakerAsset
from ..services.custom_baker_setup import CustomBakerSetupService
from ..services.parameter_service import ParameterService
from ..constant import LOG, get_prefs


class CustomBaker(BakerBase):
    """Custom bake defined in an external blend file."""

    id = "CUSTOM"
    name = "Custom"
    description = "Custom bake defined in an external blend file."
    icon = "TEXTURE"
    blender_bake_type = "EMIT"
    accumulator_id = "ALPHA_OVER"
    asset_path: Path

    @contextmanager
    def prepare_execution(self, target: bpy.types.Object) -> Generator[BakerExecution, Any, Any]:
        asset = BakerAsset(filepath=self.asset_path)

        setup = CustomBakerSetupService.prepare(asset=asset, target=target)

        try:
            yield BakerExecution(target=setup.target, setup=setup)

        finally:
            setup.cleanup()

    def apply_parameters(self, ctx: BakeContext):
        definition = registry_definition.get(self.id)
        if definition is None:
            LOG.error("Parameter definition not found")
            return

        state = ctx.task.baker_settings
        if state is None:
            LOG.error("Bake Settings not found")
            return

        snapshot = ParameterService.snapshot(definition, state)

        LOG.debug("Applying baker parameters")

        materials = ctx.materials.materials

        if materials is None:
            LOG.error(f"Material Overries not found for {ctx.target.name}")
            return

        parameter_context = ParameterContext(
            object=ctx.target,
            materials=materials,
        )

        ParameterApplier.apply(
            definition,
            snapshot,
            parameter_context,
        )

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
    prefs = get_prefs()
    for c in classes:
        for library in prefs.baker_libraries:
            LOG.info(f"Registering Library : {library.name}")
            library_root = Path(library.path)
            if not library_root.exists() or not library_root.is_dir():
                LOG.warning(f"Library path is not valid : {library_root}")
                continue

            blend_files = [f for f in library_root.iterdir() if f.is_file() and f.suffix.lower() == ".blend"]

            if len(blend_files) == 0:
                LOG.warning(f"No blend file found in {library.name} library")

            metadata_loader = MetadataLoader()
            for blend_file in blend_files:
                custom_baker = c()
                baker_name = blend_file.stem.upper().replace(" ", "_")
                custom_baker.id += f"_{baker_name}"
                custom_baker.asset_path = blend_file
                custom_baker.name = blend_file.stem.capitalize()
                LOG.info(f"Registering Custom Baker : {baker_name}")
                registry_baker.register(custom_baker)

                registry_definition.register_lazy(
                    identifier=custom_baker.id,
                    asset_path=blend_file,
                    loader=metadata_loader.load_definition,
                )


def unregister():
    for c in classes:
        registry_baker.unregister_custom(c.id)


def refresh():
    unregister()
    register()
