from __future__ import annotations

from time import perf_counter
import traceback

import bpy

from .context import BakeContext
from .job import BakeJob
from .session import BakeSession
from ..maps.registry import registry


class InternalBakeExecutor:
    """
    Executes a BakeJob inside the current Blender instance.
    """

    def __init__(self):
        self._cancel_requested = False

    def execute(self, context: bpy.types.Context, job: BakeJob) -> BakeSession:
        """
        Execute a BakeJob.

        Returns the BakeSession containing execution statistics.
        """
        session = BakeSession(context=context, job=job)

        session.initialize(context)

        job.notify_started()

        try:
            self.before_job(session)

            for task in job.tasks:
                if self._cancel_requested:
                    session.cancel()

                    break

                self.execute_task(session, task)

            self.after_job(session)

        finally:
            session.cleanup()
            session.restore(context)
            job.notify_finished()

        return session

    def execute_task(self, session: BakeSession, task) -> None:
        session.current_context = BakeContext(
            session=session,
            task=task,
            baker=registry.get(task.baker_id),
        )
        ctx = session.current_context

        session.current_task = task
        session.job.notify_task_started(task)
        start = perf_counter()

        try:
            self.before_task(ctx)

            task.baker.execute(ctx)

            ctx.succeed()

            session.job.notify_task_finished(task, True, perf_counter() - start)

        except Exception as exc:
            traceback.print_exc()

            ctx.fail(str(exc))

            session.job.notify_task_failed(task, str(exc))

        finally:
            self.after_task(ctx)

    def before_job(self, session: BakeSession) -> None:
        """
        Hook called before the first task.
        """
        pass

    def after_job(self, session: BakeSession) -> None:
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
