from __future__ import annotations

from universal_baker.executors.execution_target import ExecutionTarget

from ..constant import LOG
from ..runtime.context import ExecutionContext
from ..runtime.context_accumulate import AccumulateContext
from ..runtime.session import ExecutionSession
from ..runtime.task_accumulate import AccumulateTask
from ..core.registry_executor import registry_executor
from .executor_base import TaskExecutor
from ..logger.event import ScopeState
from ..logger_bake_middleware.bake_summary import EventCategory


class AccumulateExecutorInternal(TaskExecutor):
    """
    Executes a Job inside the current Blender instance.
    """

    id: str = "ACCUMULATE"

    def __init__(self):
        self._cancel_requested = False

    def execute_task(self, session: ExecutionSession, execution: ExecutionTarget, task: AccumulateTask) -> None:
        with LOG.scope(task.producer.name):
            ctx = AccumulateContext(
                session=session,
                task=task,
            )
            LOG.info(
                self.init_task_message(session),
                scope_state=ScopeState.ENTER,
                category=EventCategory.ACCUMULATE,
            )
            execution.execute(
                session=session,
                task=task,
                context=ctx,
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


classes = (AccumulateExecutorInternal,)


def register():
    for c in classes:
        registry_executor.register(c())


def unregister():
    for c in classes:
        registry_executor.unregister(c.id)
