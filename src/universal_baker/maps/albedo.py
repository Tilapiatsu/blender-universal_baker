from .base import BaseBaker
from ..baker.planner import BakeTask


class Baker(BaseBaker):
    def prepare(self, task: BakeTask, context):
        return super().prepare(task, context)

    def bake(self, task: BakeTask, context):
        return super().bake(task, context)

    def cleanup(self, task: BakeTask, context):
        return super().cleanup(task, context)
