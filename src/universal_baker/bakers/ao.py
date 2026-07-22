from __future__ import annotations

from .base import BakerBase

from ..runtime.context import BakeContext
from ..services.image_bake import ImageServiceBake
from ..services.material import MaterialService
from ..core.registry_baker import registry_baker


class AmbientOcclusionBaker(BakerBase):
    """Bake the diffuse/albedo color."""

    id = "AO"
    name = "Ambient Occlusion"
    description = "Bake Ambient Occlusion"
    icon = "TEXTURE"
    blender_bake_type = "AO"

    def execute(self, ctx: BakeContext) -> None:
        return super().execute(ctx)

    def prepare(self, ctx: BakeContext):
        """
        Prepare everything required before Blender's bake.
        """
        ctx.image = ImageServiceBake.acquire(ctx.image, ctx.task)
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
        """Save Pack to disk."""
        ImageServiceBake.save(ctx.image)


classes = (AmbientOcclusionBaker,)


def register():
    for c in classes:
        registry_baker.register(c())


def unregister():
    pass
