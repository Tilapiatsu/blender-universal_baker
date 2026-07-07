from .planner import BakeTask


class BakeExecutor:
    def execute(self, tasks: list[BakeTask]):
        for task in tasks:
            self.execute_task(task)

    def execute_task(self, task: BakeTask): ...
