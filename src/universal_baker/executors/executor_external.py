from __future__ import annotations

import bpy

from ..runtime.session import ExecutionSession
from ..runtime.context import BakeContext
from ..runtime.job import Job
from ..core.registry_baker import registry_baker
from ..core.registry_executor import registry_executor
from .executor_base import TaskExecutor


class BakeExecutorExternal(TaskExecutor):
    """
    Executes a Job inside the current Blender instance.
    """

    id: str = "BakeExternal"

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


class PackExecutorExternal(TaskExecutor):
    """
    Executes a Job inside the current Blender instance.
    """

    id: str = "PackExternal"

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


classes = (
    BakeExecutorExternal,
    PackExecutorExternal,
)


def register():
    for c in classes:
        registry_executor.register(c())


def unregister():
    pass
