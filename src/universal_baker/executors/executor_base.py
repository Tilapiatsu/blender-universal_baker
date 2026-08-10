from __future__ import annotations

import bpy

from abc import ABC, abstractmethod
from ..constant import LOG
from ..runtime.session import ExecutionSession
from ..runtime.context import ExecutionContext
from ..runtime.job import Job


# TODO: Need to make task Executor more generic, deduplicate code, and make it compatible with any task type -> BakeTask,
# Accumulators, Packer, Maskers
#
class TaskExecutor(ABC):
    id: str

    def execute(self, context: bpy.types.Context, job: Job) -> ExecutionSession: ...

    def finish(self, session: ExecutionSession, context: bpy.types.Context, job: Job):
        session.cleanup()
        session.restore(context)
        session.dispose()
        job.notify_finished()

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
