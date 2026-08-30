from __future__ import annotations

from .base import BakerBase

from ..enum.bake_colorspace import BakeColorSpace
from ..runtime.context_bake import BakeContext
from ..enum.image_colorspace import ImageColorSpace
from ..core.registry_baker import registry_baker


class DiffuseBaker(BakerBase):
    """Bake the diffuse/albedo color."""

    id = "DIFFUSE"
    name = "Diffuse"
    description = "Bake diffuse color"
    icon = "TEXTURE"
    blender_bake_type = "DIFFUSE"
    accumulator_id = "ALPHA_OVER"
    colorspace: ImageColorSpace = ImageColorSpace.SRGB
    clear_preview_material: bool = False

    def execute(self, ctx: BakeContext) -> None:
        return super().execute(ctx)

    def prepare_execution(self, target):
        return super().prepare_execution(target)

    def configure_preview_material(self, material): ...

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


classes = (DiffuseBaker,)


def register():
    for c in classes:
        registry_baker.register(c())


def unregister():
    for c in classes:
        registry_baker.unregister(c.id)
