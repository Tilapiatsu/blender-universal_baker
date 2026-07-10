from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from uuid import uuid4

from .task import BakeTask


class BakeJobStatus(Enum):
    """Execution state of a bake job."""

    WAITING = auto()
    RUNNING = auto()
    FINISHED = auto()
    CANCELLED = auto()
    FAILED = auto()


@dataclass(slots=True)
class BakeJob:
    """A bake job contains every bake task."""

    tasks: list[BakeTask] = field(default_factory=list)
    uid: str = field(default_factory=lambda: str(uuid4()))
    status: BakeJobStatus = BakeJobStatus.WAITING
    current_task: int = 0
    progress: float = 0.0
    errors: list[str] = field(default_factory=list)

    @property
    def total_tasks(self) -> int:
        return len(self.tasks)

    def add_task(self, task: BakeTask):
        self.tasks.append(task)

    def cancel(self):
        self.status = BakeJobStatus.CANCELLED

    def notify_started(self) -> None:
        pass

    def notify_finished(self) -> None:
        pass

    def notify_task_started(self, task: BakeTask) -> None:
        pass

    def notify_task_finished(self, task: BakeTask, log: bool, time_elapsed: float) -> None:
        pass

    def notify_task_failed(self, task: BakeTask, msg: str) -> None:
        pass

    def __repr__(self) -> str:
        result = f"""
            {"=" * 60}
            Universal Baker
            Bake Job
            {"=" * 60}\n
            """

        for index, task in enumerate(self.tasks):
            result += f"{index + 1:03d} | {task.object_name:20} | {task.baker_id}\n"

        result += "-" * 60 + "\n"

        result += f"Total Tasks : {self.total_tasks}\n"

        result += "=" * 60 + "\n"

        return result
