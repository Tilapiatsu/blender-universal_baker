from __future__ import annotations

from ..constant import LOG
from ..core.registry_baker import registry_baker
from ..core.registry_executor import registry_executor
from ..logger.event import ScopeState
from ..logger_bake_middleware.bake_summary import EventCategory
from ..runtime.baker_objects import BakerObjects
from ..runtime.context import ExecutionContext
from ..runtime.context_bake import BakeContext
from ..runtime.session import ExecutionSession
from ..runtime.task_bake import BakeTask
from .execution_target import ExecutionTarget
from .executor_base import TaskExecutor


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
            LOG.info(
                self.init_task_message(session),
                scope_state=ScopeState.ENTER,
                category=EventCategory.MASK,
            )

            ctx = BakeContext(
                session=session,
                task=task,
                baker=registry_baker[task.baker_id],
            )

            baker_objects = BakerObjects(target=ctx.target, sources=task.sources)

            # NOTE: Prepare the target in case of CustomBaker
            with task.producer.prepare_execution(baker_objects) as bake_target:
                ctx.target = bake_target.target
                ctx.sources = bake_target.sources
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


classes = (BakeExecutorInternal,)


def register():
    for c in classes:
        registry_executor.register(c())


def unregister():
    for c in classes:
        registry_executor.unregister(c.id)
