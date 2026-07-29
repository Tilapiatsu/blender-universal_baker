from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from uuid import uuid4

from ..constant import LOG
from .task import Task
from .task_bake import BakeTask
from .task_pack import PackingTask
from ..logger.middleware.statistics import StatisticsMiddleware
from ..logger.event import ScopeState


class JobStatus(Enum):
    """Execution state of a bake job."""

    WAITING = auto()
    RUNNING = auto()
    FINISHED = auto()
    CANCELLED = auto()
    FAILED = auto()


@dataclass(slots=True)
class Job:
    """A job contains every bake task."""

    tasks: list[Task] = field(default_factory=list)
    uid: str = field(default_factory=lambda: str(uuid4()))
    status: JobStatus = JobStatus.WAITING
    current_task: int = 0
    progress: float = 0.0
    errors: list[str] = field(default_factory=list)

    @property
    def total_tasks(self) -> int:
        return len(self.tasks)

    def add_task(self, task: Task):
        self.tasks.append(task)

    def cancel(self):
        self.status = JobStatus.CANCELLED

    def notify_started(self) -> None:
        pass

    def notify_finished(self) -> None:
        stats = LOG.middleware.get("StatisticsMiddleware")
        if stats is None:
            return

        LOG.info("Job ended with :")
        LOG.info(f"{stats.warning} warning(s)")
        LOG.info(f"{stats.error} error(s)")

    def notify_task_started(self, task: Task) -> None:
        self.current_task += 1

    def notify_task_finished(self, task: Task, log: bool, time_elapsed: float) -> None:
        if log:
            task.notify_finished(time_elapsed)

    def notify_task_failed(self, task: Task, time_elapsed: float, errors: tuple[str, ...]) -> None:
        task.notify_failed(time_elapsed, errors)

    def __repr__(self) -> str:
        result = f"""
{"=" * 60}
Universal Baker
Bake Job
{"=" * 60}\n
"""

        for index, task in enumerate(self.tasks):
            result += f"{index + 1:03d} | {str(task)}\n"

        result += "-" * 60 + "\n"

        result += f"Total Tasks : {self.total_tasks}\n"

        result += "=" * 60 + "\n"

        return result
