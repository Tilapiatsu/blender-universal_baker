from __future__ import annotations

import bpy

from abc import ABC, abstractmethod
from ..runtime.session import ExecutionSession
from ..runtime.context import ExecutionContext
from ..runtime.job import Job


class TaskExecutor(ABC):
    id: str

    def execute(self, context: bpy.types.Context, job: Job) -> ExecutionSession: ...

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
