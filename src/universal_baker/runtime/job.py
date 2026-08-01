from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from uuid import uuid4


from ..constant import LOG
from .task import Task
from ..logger.severity import Severity


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
        LOG.info("Job Started")

    def notify_finished(self) -> None:
        stats = LOG.middleware.get("StatisticsMiddleware")
        if stats is not None:
            if stats.warning > 0 or stats.error > 0:
                LOG.info("Job ended with :")
            else:
                LOG.info("Job finished successfully!")
            if stats.warning > 0:
                LOG.warning(f"{stats.warning} warning(s)")
            if stats.error > 0:
                LOG.error(f"{stats.error} error(s)")

        summary = LOG.middleware.get("BakeSummaryMiddleware")
        if summary is not None:
            LOG.separator(Severity.INFO)
            LOG.info("Job Summary : ")
            for s in summary.successes:
                message = ""
                if "object" in s.data.keys():
                    message += f"{s.data['object']:20} | "

                message += f"{s.scope[-1]} {s.message:30} ({s.scope_duration:.2f}s)"
                LOG.info(message)

            for f in summary.failures:
                message = ""
                if "object" in f.data.keys():
                    message += f"{f.data['object']:20} | "

                message += f"{f.scope[-1]} {f.message:30} ({f.scope_duration:.2f}s)"
                LOG.error(message)

            summary.clear()

        LOG.separator(Severity.INFO)

    def notify_task_started(self, task: Task) -> None:
        self.current_task += 1

    def notify_task_finished(self, task: Task, log: bool, time_elapsed: float) -> None:
        if log:
            task.notify_finished(time_elapsed)

    def notify_task_failed(self, task: Task, time_elapsed: float, error: str) -> None:
        task.notify_failed(time_elapsed, error)

    def __repr__(self) -> str:
        return self.job_summary()

    def job_summary(self) -> str:
        result = f"""
{"=" * 60}
Universal Baker
Bake Job
{"=" * 60}\n
"""

        for index, task in enumerate(self.tasks):
            result += f"{index + 1:03d} | {str(task)}\n"

        result += "-" * 100 + "\n"

        result += f"Total Tasks : {self.total_tasks}\n"

        result += "=" * 100 + "\n"

        return result
