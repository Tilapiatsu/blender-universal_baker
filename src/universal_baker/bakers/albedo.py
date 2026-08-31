from __future__ import annotations

from typing import TYPE_CHECKING

from ..enum.image_colorspace import ImageColorSpace
from ..runtime.context_bake import BakeContext
from .base import BakerBase

if TYPE_CHECKING:
    from ..parameter.metadata import ParameterMetadata


class Baker(BakerBase):
    colorspace: ImageColorSpace = ImageColorSpace.SRGB
    clear_preview_material: bool = False

    @property
    def parameters(self) -> tuple[ParameterMetadata, ...]:
        return super().parameters

    def prepare_execution(self, target):
        return super().prepare_execution(target)

    def prepare(self, ctx: BakeContext):
        """
        Prepare everything required before Blender's bake.
        """
        return super().prepare(ctx)

    def configure_preview_material(self, material): ...

    def bake(self, ctx: BakeContext):
        """Execute the bake."""
        return super().bake(ctx)

    def cleanup(self, ctx: BakeContext):
        """
        Cleanup after baking.
        """
        return super().cleanup(ctx)

    def update_baker(self, ctx: BakeContext) -> None:
        return super().update_baker(ctx)

    def export_file(self, ctx: BakeContext):
        """Save Bake to disk."""
        return super().export_file(ctx)
