from __future__ import annotations

from universal_baker.runtime.context_evaluate_mesh import EvaluateMeshesContext

from ..constant import LOG
from ..core.registry_executor import registry_executor
from ..logger.event import ScopeState
from ..logger_bake_middleware.bake_summary import EventCategory
from ..runtime.context import ExecutionContext
from ..runtime.context_ownership_mask import OwnershipMaskContext
from ..runtime.session import ExecutionSession
from ..runtime.task_evaluate_mesh import EvaluateMeshesTask
from .execution_target import ExecutionTarget
from .executor_base import TaskExecutor


class EvaluateMeshesExecutorInternal(TaskExecutor):
    """
    Executes a Job inside the current Blender instance.
    """

    id: str = "EVALUATE_MESHES"

    def __init__(self):
        self._cancel_requested = False

    def execute_task(self, session: ExecutionSession, execution: ExecutionTarget, task: EvaluateMeshesTask) -> None:
        with LOG.scope(
            task.name,
        ):
            LOG.info(
                self.init_task_message(session),
                scope_state=ScopeState.ENTER,
                category=EventCategory.EVALUATE_MESHES,
            )
            ctx = EvaluateMeshesContext(
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


classes = (EvaluateMeshesExecutorInternal,)


def register():
    for c in classes:
        registry_executor.register(c())


def unregister():
    for c in classes:
        registry_executor.unregister(c.id)
