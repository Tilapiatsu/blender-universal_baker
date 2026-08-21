from __future__ import annotations
from contextlib import ContextDecorator

import bpy

from .base import BakerBase

from ..runtime.baker_setup import BakerSetup
from ..runtime.context_bake import BakeContext
from ..core.registry_baker import registry_baker
from ..resources.baker_asset import BakerAsset
from ..services.custom_baker_setup import CustomBakerSetupService
from pathlib import Path


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
    for c in classes:
        registry_baker.register(c())


def unregister():
    pass
