from __future__ import annotations

from .base import BakerBase

from ..runtime.context import BakeContext
from ..services.image_bake import ImageServiceBake
from ..services.material import MaterialService
from ..core.registry_baker import registry_baker


class DiffuseBaker(BakerBase):
    """Bake the diffuse/albedo color."""

    id = "DIFFUSE"
    name = "Diffuse"
    description = "Bake diffuse color"
    icon = "TEXTURE"
    blender_bake_type = "DIFFUSE"

    def execute(self, ctx: BakeContext) -> None:
        return super().execute(ctx)

    def prepare(self, ctx: BakeContext):
        """
        Prepare everything required before Blender's bake.
        """
        ImageServiceBake.acquire(ctx.image, ctx.task)
        MaterialService.prepare_target(ctx)

    def bake(self, ctx: BakeContext) -> None:
        return super().bake(ctx)

    def cleanup(self, ctx: BakeContext):
        """
        Cleanup after baking.
        """
        MaterialService.restore_target(ctx)
        ImageServiceBake.cleanup(ctx.image)

    def update_baker(self, ctx: BakeContext) -> None:
        return super().update_baker(ctx)

    def export_file(self, ctx: BakeContext):
        """Save Bake to disk."""
        ImageServiceBake.save(ctx.image)


classes = (DiffuseBaker,)


def register():
    for c in classes:
        registry_baker.register(c())


def unregister():
    pass
