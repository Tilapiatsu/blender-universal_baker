from __future__ import annotations

from ..constant import LOG
from ..runtime.context import ExecutionContext
from ..runtime.session import ExecutionSession
from ..runtime.context_mask import MaskContext
from ..runtime.task_mask_buffer import MaskBufferTask
from ..core.registry_executor import registry_executor
from .executor_base import TaskExecutor
from ..logger.event import ScopeState
from ..logger_bake_middleware.bake_summary import EventCategory
from .execution_target import ExecutionTarget


class MaskExecutorInternal(TaskExecutor):
    """
    Executes a Job inside the current Blender instance.
    """

    id: str = "MASK"

    def __init__(self):
        self._cancel_requested = False

    def execute_task(self, session: ExecutionSession, execution: ExecutionTarget, task: MaskBufferTask) -> None:
        with LOG.scope(
            task.name,
            width=task.output_context.output_settings.path.width,
            height=task.output_context.output_settings.path.height,
        ):
            LOG.info(
                self.init_task_message(session),
                scope_state=ScopeState.ENTER,
                category=EventCategory.MASK,
            )
            ctx = MaskContext(
                session=session,
                task=task,
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


classes = (MaskExecutorInternal,)


def register():
    for c in classes:
        registry_executor.register(c())


def unregister():
    for c in classes:
        registry_executor.unregister(c.id)
