from __future__ import annotations

from .base import AccumulatorBase

from ..runtime.context_accumulate import AccumulateContext
from ..services.image_bake import ImageServiceBake
from ..core.registry_accumulator import registry_accumulator


class AlphaOverAccumulator(AccumulatorBase):
    """Accumulate images using their alpha channel."""

    id = "ALPHA_OVER"
    name = "Alpha Over"
    description = "Accumulate image using their alpha channel"
    icon = "NODE_COMPOSITING"

    def execute(self, ctx: AccumulateContext) -> None:
        return super().execute(ctx)

    def prepare(self, ctx: AccumulateContext):
        """
        Prepare everything required before Blender's accumulate.
        """
        super().prepare(ctx)

    def accumulate(self, ctx: AccumulateContext) -> None:
        """Execute the Accumulator."""
        return super().accumulate(ctx)

    def cleanup(self, ctx: AccumulateContext):
        """
        Cleanup after Accumulator.
        """
        super().cleanup(ctx)

    def update_baker(self, ctx: AccumulateContext) -> None:
        # TODO : Is this still necessary
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
