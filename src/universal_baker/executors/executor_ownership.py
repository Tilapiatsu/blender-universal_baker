from __future__ import annotations

from ..constant import LOG
from ..core.registry_executor import registry_executor
from ..logger.event import ScopeState
from ..logger_bake_middleware.bake_summary import EventCategory
from ..runtime.context import ExecutionContext
from ..runtime.session import ExecutionSession
from ..runtime.task_ownership_mask import UvOwnershipTask
from ..runtime.context_ownership_mask import OwnershipMaskContext
from .executor_base import TaskExecutor
from .execution_target import ExecutionTarget


class OwnershipMaskExecutorInternal(TaskExecutor):
    """
    Executes a Job inside the current Blender instance.
    """

    id: str = "UV_OWNERSHIP"

    def __init__(self):
        self._cancel_requested = False

    def execute_task(self, session: ExecutionSession, execution: ExecutionTarget, task: UvOwnershipTask) -> None:
        with LOG.scope(
            task.name,
            width=task.output_context.output_settings.path.width,
            height=task.output_context.output_settings.path.height,
        ):
            ctx = OwnershipMaskContext(
                session=session,
                task=task,
            )
            execution.execute(
                session=session,
                task=task,
                context=ctx,
                scope_state=ScopeState.ENTER,
                event_category=EventCategory.MASK,
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


classes = (OwnershipMaskExecutorInternal,)


def register():
    for c in classes:
        registry_executor.register(c())


def unregister():
    pass
