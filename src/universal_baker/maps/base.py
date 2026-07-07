from ..baker.planner import BakeTask
from typing import Protocol


class BaseBaker(Protocol):
    id = ""
    label = ""

    def prepare(self, task: BakeTask, context): ...

    def bake(self, task: BakeTask, context): ...

    def cleanup(self, task: BakeTask, context): ...
