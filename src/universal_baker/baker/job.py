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
