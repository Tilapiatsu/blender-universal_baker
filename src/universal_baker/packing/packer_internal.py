from __future__ import annotations

from ..runtime.context import ExecutionContext
from .packer_base import Packer


class PackerInternal(Packer):
    def execute(self, ctx: ExecutionContext):
        pass
