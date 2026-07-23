from .base import BakerBase
from ..runtime.context import BakeContext


class Baker(BakerBase):
    def prepare(self, ctx: BakeContext):
        """
        Prepare everything required before Blender's bake.
        """
        return super().prepare(ctx)

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

    def create_output(self, ctx: BakeContext):
        return super().create_output(ctx)

    def export_file(self, ctx: BakeContext):
        """Save Bake to disk."""
        return super().export_file(ctx)
