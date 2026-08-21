from __future__ import annotations

from pathlib import Path
import bpy

from .base import BakerBase

from ..runtime.baker_setup import BakerSetup
from ..runtime.context_bake import BakeContext
from ..core.registry_baker import registry_baker
from ..resources.baker_asset import BakerAsset
from ..services.custom_baker_setup import CustomBakerSetupService
from ..constant import LOG, get_prefs


class CustomBaker(BakerBase):
    """Custom bake defined in an external blend file."""

    id = "CUSTOM"
    name = "Custom"
    description = "Custom bake defined in an external blend file."
    icon = "TEXTURE"
    blender_bake_type = "NONE"
    accumulator_id = "ALPHA_OVER"
    asset_path: Path

    def prepare_execution(self, target: bpy.types.Object) -> BakerSetup:
        # TODO: Need to pipe the asset path for the custom baker
        asset = BakerAsset(
            filepath=self.asset_path,
        )

        setup_service = CustomBakerSetupService()
        context = setup_service.prepare(
            asset=asset,
            target=target,
        )
        return context

    def execute(self, ctx: BakeContext) -> None:
        return super().execute(ctx)

    def configure_preview_material(self, material):
        # TODO: to be writen
        super().configure_preview_material(material)

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

            for blend_file in blend_files:
                custom_baker = c()
                baker_name = blend_file.stem.upper().replace(" ", "_")
                custom_baker.id += f"_{baker_name}"
                custom_baker.asset_path = blend_file
                LOG.info(f"Registering Custom Baker : {baker_name}")
                registry_baker.register(custom_baker)


def unregister():
    for c in classes:
        registry_baker.unregister_custom(c.id)


def refresh():
    unregister()
    register()
