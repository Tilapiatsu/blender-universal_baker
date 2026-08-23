from __future__ import annotations

from time import perf_counter
import traceback


from .execution_target import ExecutionTarget

from ..enum.execution import Execution
from ..constant import LOG
from ..runtime.session import ExecutionSession
from ..runtime.context import ExecutionContext
from ..core.registry_execution import registry_execution


class ExecutorInternal(ExecutionTarget):
    execution: Execution = Execution.INTERNAL

    def execute(
        self,
        session: ExecutionSession,
        task,
        context: ExecutionContext,
    ) -> None:
        session.current_context = context
        ctx = session.current_context
        session.current_task = task
        session.job.notify_task_started(task)
        start = perf_counter()

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


classes = (ExecutorInternal,)


def register():
    for c in classes:
        registry_execution.register(c())


def unregister():
    for c in classes:
        registry_execution.unregister(c.execution)
