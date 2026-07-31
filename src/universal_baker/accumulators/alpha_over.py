from __future__ import annotations

from .base import AccumulatorBase

from ..runtime.context_accumulate import AccumulateContext
from ..services.image_bake import ImageServiceBake
from ..core.registry_accumulator import registry_accumulator


class AlphaOverAccumulator(AccumulatorBase):
    """Bake the diffuse/albedo color."""

    id = "ALPHA_OVER"
    name = "Alpha Over"
    description = "Accumulate image using their alpha channel"
    icon = "NODE_COMPOSITING"

    def execute(self, ctx: AccumulateContext) -> None:
        return super().execute(ctx)

    def prepare(self, ctx: AccumulateContext):
        """
        Prepare everything required before Blender's bake.
        """
        super().prepare(ctx)
        ctx.image = ImageServiceBake.acquire(ctx.image, ctx.task)

    def accumulate(self, ctx: AccumulateContext) -> None:
        """Execute the bake."""
        return super().accumulate(ctx)

    def cleanup(self, ctx: AccumulateContext):
        """
        Cleanup after baking.
        """
        super().cleanup(ctx)
        ImageServiceBake.cleanup(ctx.image)

    def update_baker(self, ctx: AccumulateContext) -> None:
        return super().update_baker(ctx)

    def create_artifact(self, ctx: AccumulateContext) -> None:
        return super().create_artifact(ctx)

    def export_file(self, ctx: AccumulateContext):
        """Save Pack to disk."""
        super().export_file(ctx)


classes = (AlphaOverAccumulator,)


def register():
    for c in classes:
        registry_accumulator.register(c())


def unregister():
    pass
