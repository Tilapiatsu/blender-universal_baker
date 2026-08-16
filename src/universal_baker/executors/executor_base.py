from __future__ import annotations

from time import perf_counter
import traceback
from abc import ABC
from typing import Callable

import bpy

from universal_baker.logger.event import ScopeState
from universal_baker.logger_bake_middleware.bake_summary import EventCategory
from ..constant import LOG
from ..runtime.session import ExecutionSession
from ..runtime.context import ExecutionContext
from ..runtime.job import Job


class TaskExecutor(ABC):
    id: str
    task_types: list[Callable]
    _task_type_names: list[str] | None = None

    @property
    def task_type_names(self) -> list[str]:
        if self._task_type_names is None:
            self._task_type_names = [t.__name__ for t in self.task_types]
        return self._task_type_names

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
                    if type(task).__name__ not in self.task_type_names:
                        continue
                    if self._cancel_requested:
                        session.cancel()

                        break

                    self.execute_task(session, task)

                self.after_job(session)

            finally:
                self.finish(session, context, job)

            return session

    def execute_task(self, session: ExecutionSession, task) -> None: ...

    def _execute(
        self,
        session: ExecutionSession,
        task,
        context: ExecutionContext,
        scope_state: ScopeState,
        event_category: EventCategory,
    ) -> None:
        session.current_context = context
        ctx = session.current_context
        session.current_task = task
        session.job.notify_task_started(task)
        start = perf_counter()
        LOG.info(
            self.init_task_message(session),
            scope_state=ScopeState.ENTER,
            category=EventCategory.MASK,
        )

        try:
            self.before_task(ctx)
            task.producer.execute(ctx)
            ctx.succeed(f"{task.producer.name} succeeded")
            session.job.notify_task_finished(task, True, perf_counter() - start)

        except Exception as exc:
            traceback.print_exc()
            ctx.fail(f"{task.producer.name} failed" + str(exc))
            session.job.notify_task_failed(
                task,
                perf_counter() - start,
                str(exc),
            )

        finally:
            self.after_task(ctx)

    def finish(self, session: ExecutionSession, context: bpy.types.Context, job: Job):
        session.cleanup()
        session.restore(context)
        session.dispose()
        job.notify_finished()

    def init_task_message(self, session) -> str:
        return f"{'=' * 100} Task {session.job.current_task} / {session.job.total_tasks} {'=' * 100}"

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
