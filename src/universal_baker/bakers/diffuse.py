from __future__ import annotations

from .base import BaseBaker

from ..runtime.context import BakeContext
from ..services.image import ImageService
from ..services.material import MaterialService
from ..core.registry import registry


class DiffuseBaker(BaseBaker):
    """Bake the diffuse/albedo color."""

    id = "DIFFUSE"
    label = "Diffuse"
    description = "Bake diffuse color"
    icon = "TEXTURE"
    blender_type = "DIFFUSE"

    def execute(self, ctx: BakeContext) -> None:
        return super().execute(ctx)

    def prepare(self, ctx: BakeContext):
        """
        Prepare everything required before Blender's bake.
        """
        ctx.image = ImageService.acquire(ctx)
        MaterialService.prepare_target(ctx)

    def bake(self, ctx: BakeContext) -> None:
        return super().bake(ctx)

    def cleanup(self, ctx: BakeContext):
        """
        Cleanup after baking.
        """
        MaterialService.restore_target(ctx)
        ImageService.cleanup(ctx)


classes = (DiffuseBaker,)


def register():
    for c in classes:
        registry.register(c())


def unregister():
    pass
