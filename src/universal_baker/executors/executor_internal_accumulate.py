from __future__ import annotations

from time import perf_counter
import traceback

import bpy

from ..constant import LOG
from ..runtime.context import ExecutionContext
from ..runtime.context_accumulate import AccumulateContext
from ..runtime.session import ExecutionSession
from ..runtime.task_accumulate import AccumulateTask
from ..core.registry_executor import registry_executor
from .executor_base import TaskExecutor
from ..logger.event import ScopeState
from ..logger_bake_middleware.bake_summary import EventCategory
from ..runtime.job import Job


class AccumulateExecutorInternal(TaskExecutor):
    """
    Executes a Job inside the current Blender instance.
    """

    id: str = "AccumulateInternal"

    def __init__(self):
        self._cancel_requested = False

    def execute(self, context: bpy.types.Context, job: Job) -> ExecutionSession:
        """
        Execute a Job.

        Returns the ExecutionSession containing execution statistics.
        """
        with LOG.scope(self.id):
            session = ExecutionSession(context=context, job=job)
            session.initialize(context)
            job.notify_started()

            try:
                self.before_job(session)

                for task in job.tasks:
                    if not isinstance(task, AccumulateTask):
                        continue
                    if self._cancel_requested:
                        session.cancel()

                        break

                    self.execute_task(session, task)

                self.after_job(session)

            finally:
                self.finish(session, context, job)

            return session

    def execute_task(self, session: ExecutionSession, task: AccumulateTask) -> None:
        with LOG.scope(task.accumulator.name):
            session.current_context = AccumulateContext(
                session=session,
                task=task,
            )
            ctx = session.current_context
            session.current_task = task
            session.job.notify_task_started(task)
            start = perf_counter()
            LOG.info(
                f"Init Task {session.job.current_task} / {session.job.total_tasks}",
                scope_state=ScopeState.ENTER,
                category=EventCategory.ACCUMULATE,
            )
            LOG.info("=" * 100)

            try:
                self.before_task(ctx)
                task.accumulator.execute(ctx)
                ctx.succeed(f"{task.accumulator.name} succeeded")
                session.job.notify_task_finished(task, True, perf_counter() - start)

            except Exception as exc:
                traceback.print_exc()
                ctx.fail(f"{task.accumulator.name} failed\n" + str(exc))
                session.job.notify_task_failed(
                    task,
                    perf_counter() - start,
                    str(exc),
                )

            finally:
                self.after_task(ctx)

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
    pass
