from __future__ import annotations

from typing import Callable

import bpy

from ..constant import LOG
from ..runtime.context import ExecutionContext
from ..runtime.session import ExecutionSession
from ..enum.execution import Execution
from ..runtime.job import Job
from ..core.registry_executor import registry_executor
from ..core.registry_execution import registry_execution


class Executor:
    """
    Executes a Job and makes sure it executes the with the prope execution method.
    """

    task_types: list[Callable]
    _task_type_names: list[str] | None = None
    execution: Execution = Execution.INTERNAL

    @property
    def task_type_names(self) -> list[str]:
        if self._task_type_names is None:
            self._task_type_names = [t.__name__ for t in self.task_types]
        return self._task_type_names

    def __init__(self, execution: Execution, task_types: list[Callable]) -> None:
        self._cancel_requested = False
        self.execution = execution
        self.task_types = task_types

    def execute(self, context: bpy.types.Context, job: Job) -> ExecutionSession:
        """
        Execute a Job.

        Returns the ExecutionSession containing execution statistics.
        """
        with LOG.scope(self.execution.value):
            session = ExecutionSession(context=context, job=job)
            session.initialize(context)
            job.notify_started()

            execution = registry_execution[self.execution]

            try:
                self.before_job(session)

                for task in job.tasks:
                    # Filtering tasks by types
                    if type(task).__name__ not in self.task_type_names:
                        continue

                    if self._cancel_requested:
                        session.cancel()
                        break

                    executor = registry_executor[task.id]

                    executor.execute_task(
                        session=session,
                        execution=execution,
                        task=task,
                    )

                self.after_job(session)

            finally:
                self.finish(session, context, job)

            return session

    def finish(self, session: ExecutionSession, context: bpy.types.Context, job: Job):
        session.cleanup()
        session.restore(context)
        session.dispose()
        job.notify_finished()

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
