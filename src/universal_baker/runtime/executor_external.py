from __future__ import annotations

import bpy

from .session import ExecutionSession
from .context import BakeContext
from .job import Job


class BakeExecutorExternal:
    """
    Executes a Job inside the current Blender instance.
    """

    def __init__(self):
        self._cancel_requested = False

    def execute(self, context: bpy.types.Context, job: Job) -> ExecutionSession:
        """
        Execute a Job.

        Returns the ExecutionSession containing execution statistics.
        """
        print("execute external job")
        raise NotImplementedError

    def execute_task(self, session: ExecutionSession, task) -> None:
        print("execute external Task")

        raise NotImplementedError

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

    def before_task(self, ctx: BakeContext) -> None:
        """
        Hook called before every task.
        """
        pass

    def after_task(self, ctx: BakeContext) -> None:
        """
        Hook called after every task.
        """
        pass

    def cancel(self) -> None:
        self._cancel_requested = True

    @property
    def cancelled(self) -> bool:
        return self._cancel_requested
