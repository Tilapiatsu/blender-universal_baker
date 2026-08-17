from __future__ import annotations

from abc import ABC

from .execution_target import ExecutionTarget

from ..constant import LOG
from ..runtime.session import ExecutionSession
from ..runtime.context import ExecutionContext


class TaskExecutor(ABC):
    id: str

    def execute_task(self, session: ExecutionSession, execution: ExecutionTarget, task) -> None: ...

    def init_task_message(self, session) -> str:
        return f"{'=' * 100} Task {session.job.current_task} / {session.job.total_tasks} {'=' * 100}"

    def before_job(self, session: ExecutionSession) -> None:
        """
        Hook called before the first task.
        """
        pass

    def after_job(self, session: ExecutionSession) -> None:
        """
        Hook called after the last task.
        """
        pass

    def before_task(self, ctx: ExecutionContext) -> None:
        """
        Hook called before every task.
        """
        pass

    def after_task(self, ctx: ExecutionContext) -> None:
        """
        Hook called after every task.
        """
        pass

    def cancel(self) -> None:
        self._cancel_requested = True

    @property
    def cancelled(self) -> bool:
        return self._cancel_requested
