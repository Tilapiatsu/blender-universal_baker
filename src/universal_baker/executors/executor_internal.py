from __future__ import annotations

from time import perf_counter
import traceback

import bpy

from ..runtime.context import BakeContext, ExecutionContext, PackContext
from ..runtime.job import Job
from ..runtime.session import ExecutionSession
from ..runtime.task_bake import BakeTask
from ..runtime.task_pack import PackingTask
from ..core.registry_baker import registry_baker
from ..core.registry_executor import registry_executor
from .executor_base import TaskExecutor


class BakeExecutorInternal(TaskExecutor):
    """
    Executes a Job inside the current Blender instance.
    """

    id: str = "BakeInternal"

    def __init__(self):
        self._cancel_requested = False

    def execute(self, context: bpy.types.Context, job: Job) -> ExecutionSession:
        """
        Execute a Job.

        Returns the ExecutionSession containing execution statistics.
        """
        session = ExecutionSession(context=context, job=job)
        session.initialize(context)
        job.notify_started()

        try:
            self.before_job(session)

            for task in job.tasks:
                if not isinstance(task, BakeTask):
                    continue
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

    def execute_task(self, session: ExecutionSession, task: BakeTask) -> None:
        session.current_context = BakeContext(
            session=session,
            task=task,
            baker=registry_baker[task.baker_id],
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


class PackExecutorInternal(TaskExecutor):
    """
    Executes a Job inside the current Blender instance.
    """

    id: str = "PackInternal"

    def __init__(self):
        self._cancel_requested = False

    def execute(self, context: bpy.types.Context, job: Job) -> ExecutionSession:
        """
        Execute a Job.

        Returns the ExecutionSession containing execution statistics.
        """
        session = ExecutionSession(context=context, job=job)
        session.initialize(context)
        job.notify_started()

        try:
            self.before_job(session)

            for task in job.tasks:
                if not isinstance(task, PackingTask):
                    continue
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

    def execute_task(self, session: ExecutionSession, task: PackingTask) -> None:
        session.current_context = PackContext(
            session=session,
            task=task,
        )
        ctx = session.current_context
        session.current_task = task
        session.job.notify_task_started(task)
        start = perf_counter()

        try:
            self.before_task(ctx)
            task.packer.execute(ctx)
            ctx.succeed()
            session.job.notify_task_finished(task, True, perf_counter() - start)

        except Exception as exc:
            traceback.print_exc()
            ctx.fail(str(exc))
            session.job.notify_task_failed(task, str(exc))

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


classes = (
    BakeExecutorInternal,
    PackExecutorInternal,
)


def register():
    for c in classes:
        registry_executor.register(c())


def unregister():
    pass
