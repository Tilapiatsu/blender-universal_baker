from __future__ import annotations

from typing import Callable

from ..constant import LOG
from ..runtime.context import ExecutionContext
from ..runtime.context_pack import PackContext
from ..runtime.session import ExecutionSession
from ..runtime.task_pack import PackingTask
from ..core.registry_executor import registry_executor
from .executor_base import TaskExecutor
from ..logger.event import ScopeState
from ..logger_bake_middleware.bake_summary import EventCategory


class PackExecutorInternal(TaskExecutor):
    """
    Executes a Job inside the current Blender instance.
    """

    id: str = "PackInternal"
    task_types: list[Callable] = [PackingTask]

    def __init__(self):
        self._cancel_requested = False

    def execute_task(self, session: ExecutionSession, task: PackingTask) -> None:
        with LOG.scope(task.producer.name):
            ctx = PackContext(
                session=session,
                task=task,
            )
            self._execute(
                session=session,
                task=task,
                context=ctx,
                scope_state=ScopeState.ENTER,
                event_category=EventCategory.PACK,
            )

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


classes = (PackExecutorInternal,)


def register():
    for c in classes:
        registry_executor.register(c())


def unregister():
    pass
