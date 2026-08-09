from __future__ import annotations


from .base import MaskerBase

from ..core.registry_masker import registry_masker
from ..runtime.context_mask import MaskContext


class UvBoundryMasker(MaskerBase):
    """Accumulate images using their alpha channel."""

    id = "APPLY_MASK"
    name = "Apply Mask"
    description = "Mask image with the alpha channel of the mask"

    def execute(self, ctx: MaskContext) -> None:
        return super().execute(ctx)

    def prepare(self, ctx: MaskContext):
        """
        Prepare everything required before Blender's accumulate.
        """
        super().prepare(ctx)

    def masking(self, ctx: MaskContext) -> None:
        """Execute the Accumulator."""
        return super().masking(ctx)

    def cleanup(self, ctx: MaskContext):
        """
        Cleanup after Accumulator.
        """
        super().cleanup(ctx)

    def update_baker(self, ctx: MaskContext) -> None:
        # TODO : Is this still necessary
        return super().update_baker(ctx)

    def create_artifact(self, ctx: MaskContext) -> None:
        return super().create_artifact(ctx)

    def export_file(self, ctx: MaskContext):
        """Save Pack to disk."""
        super().export_file(ctx)


classes = (UvBoundryMasker,)


def register():
    for c in classes:
        registry_masker.register(c())


def unregister():
    pass
