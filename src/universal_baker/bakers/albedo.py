from .base import BakerBase
from ..runtime.context import BakeContext


class Baker(BakerBase):
    def prepare(self, ctx: BakeContext):
        return super().prepare(ctx)

    def bake(self, ctx: BakeContext):
        return super().bake(ctx)

    def cleanup(self, ctx: BakeContext):
        return super().cleanup(ctx)
