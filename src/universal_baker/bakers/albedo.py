from .base import BaseBaker
from ..runtime.context import BakeContext


class Baker(BaseBaker):
    def prepare(self, ctx: BakeContext):
        return super().prepare(ctx)

    def bake(self, ctx: BakeContext):
        return super().bake(ctx)

    def cleanup(self, ctx: BakeContext):
        return super().cleanup(ctx)
