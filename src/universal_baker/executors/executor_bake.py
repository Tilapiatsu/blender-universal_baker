from __future__ import annotations

from ..constant import LOG
from ..runtime.context import ExecutionContext
from ..runtime.context_bake import BakeContext
from ..runtime.session import ExecutionSession
from ..runtime.task_bake import BakeTask
from ..core.registry_baker import registry_baker
from ..core.registry_executor import registry_executor
from .executor_base import TaskExecutor
from ..logger.event import ScopeState
from ..logger_bake_middleware.bake_summary import EventCategory
from .execution_target import ExecutionTarget


class BakeExecutorInternal(TaskExecutor):
    """
    Executes a Job inside the current Blender instance.
    """

    id: str = "BAKE"

    def __init__(self):
        self._cancel_requested = False

    def execute_task(self, session: ExecutionSession, execution: ExecutionTarget, task: BakeTask) -> None:
        with LOG.scope(
            task.baker_name,
            object=task.object_name,
            baker=task.producer.name,
            width=task.output_context.output_settings.path.width,
            height=task.output_context.output_settings.path.height,
        ):
            ctx = BakeContext(
                session=session,
                task=task,
                baker=registry_baker[task.baker_id],
            )
            # NOTE: Prepare the target in case of CustomBaker
            with task.producer.prepare_execution(ctx.target) as bake_target:
                ctx.target = bake_target
                execution.execute(
                    session=session,
                    task=task,
                    context=ctx,
                    scope_state=ScopeState.ENTER,
                    event_category=EventCategory.BAKE,
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


classes = (BakeExecutorInternal,)


def register():
    for c in classes:
        registry_executor.register(c())


def unregister():
    for c in classes:
        registry_executor.unregister(c.id)
