from __future__ import annotations

import bpy

from .session import BakeSession
from .context import BakeContext
from .job import BakeJob


class BakeExecutorExternal:
    """
    Executes a BakeJob inside the current Blender instance.
    """

    def __init__(self):
        self._cancel_requested = False

    def execute(self, context: bpy.types.Context, job: BakeJob) -> BakeSession:
        """
        Execute a BakeJob.

        Returns the BakeSession containing execution statistics.
        """
        print("execute external job")
        raise NotImplementedError

    def execute_task(self, session: BakeSession, task) -> None:
        print("execute external Task")

        raise NotImplementedError

    def before_job(self, session: BakeSession) -> None:
        """
        Hook called before the first task.
        """
        pass

    def after_job(self, session: BakeSession) -> None:
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
