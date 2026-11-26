from __future__ import annotations

import traceback
from collections.abc import Callable, Iterator
from time import perf_counter

import bpy

from ..constant import LOG
from ..core.registry_execution import registry_execution
from ..core.registry_executor import registry_executor
from ..enum.execution import Execution
from ..logger.blender.modal import ModalTaskRunner, TaskProgress
from ..logger.scopes.task_scope import TaskCancelled
from ..runtime.context import ExecutionContext
from ..runtime.job import Job, JobStatus
from ..runtime.runtime_manager import RuntimeManager
from ..runtime.session import ExecutionSession
from ..runtime.task_bake import BakeTask
from .execution_target import ExecutionTarget


class Executor:
    """Executes a Job using synchronous or Blender-modal scheduling."""

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
        self.start: float = 0.0
        self._modal_runner: ModalTaskRunner | None = None

    def start_job(self, context: bpy.types.Context, job: Job):
        """Use modal execution for in-process Blender work.

        External execution retains the existing synchronous path because its
        process/IPC lifecycle is owned by the external execution target.
        """
        if self.execution is Execution.INTERNAL:
            return self.execute_modal(context, job)
        return self.execute(context, job)

    def execute(self, context: bpy.types.Context, job: Job) -> ExecutionSession:
        """Execute a Job synchronously (kept for scripts and external mode)."""
        self._cancel_requested = False
        session = ExecutionSession(context=context, job=job)
        session.initialize(context)
        job.status = JobStatus.RUNNING
        job.notify_started()
        self.start = perf_counter()
        execution = registry_execution[self.execution]

        with job.scope:
            try:
                self._execute_tasks_sync(session, execution, job)
            finally:
                if job.status is JobStatus.RUNNING:
                    job.status = JobStatus.FINISHED
                self.finish(session, context, job)
        return session

    def execute_modal(self, context: bpy.types.Context, job: Job) -> ModalTaskRunner:
        """Schedule the job as bounded task steps on Blender's event loop.

        A complete task executor call is currently one step. The UI can redraw
        and process cancellation between tasks, but a long Blender operator
        inside an individual task remains synchronous and cannot be interrupted.
        """
        if self._modal_runner is not None and not self._modal_runner._finished:
            raise RuntimeError("This Executor already has a running modal job")
        self._cancel_requested = False
        runner = ModalTaskRunner(
            LOG,
            interval=0.05,
            steps_per_tick=1,
            on_error=lambda exc: traceback.print_exception(type(exc), exc, exc.__traceback__),
            on_cancel=lambda: job.cancel(),
        )
        self._modal_runner = runner
        runner.start(context, self._execute_steps(context, job), scope=job.scope)
        return runner

    def _execute_steps(self, context: bpy.types.Context, job: Job) -> Iterator[TaskProgress]:
        """Generator whose yields occur only after all nested scopes have exited."""
        session: ExecutionSession | None = None
        session_initialized = False
        self.start = perf_counter()
        try:
            session = ExecutionSession(context=context, job=job)
            session.initialize(context)
            session_initialized = True
            job.status = JobStatus.RUNNING
            job.notify_started()
            execution = registry_execution[self.execution]
            self.before_job(session)

            if BakeTask in self.task_types:
                cage_visualization = RuntimeManager.current(context).cage_visualization
                cage_visualization.do_suspend()
                with session.runtime.bake_visualization.suspend():
                    yield from self._execute_tasks_modal(session, execution, job)
            else:
                yield from self._execute_tasks_modal(session, execution, job)

            self.after_job(session)
            if job.status is JobStatus.RUNNING:
                job.status = JobStatus.FINISHED
            return session

        except TaskCancelled:
            job.cancel()
            self._cancel_pending_tasks(job)
            if session is not None:
                session.cancel()
            raise
        except GeneratorExit:
            # ModalTaskRunner closes a suspended generator on user cancel.
            job.cancel()
            self._cancel_pending_tasks(job)
            if session is not None:
                session.cancel()
            raise
        except BaseException as exc:
            job.status = JobStatus.FAILED
            self._cancel_pending_tasks(job)
            job.errors.append(str(exc))
            job.notify_failed(perf_counter() - self.start, str(exc))
            raise
        finally:
            if session is not None:
                self.finish(session, context, job, restore=session_initialized)

    @staticmethod
    def _cancel_pending_tasks(job: Job) -> None:
        """Mark planned-but-unstarted task scopes as cancelled in the UI tree."""
        from ..logger.scopes.task_status import TaskStatus

        for task in job.tasks:
            if task.scope.status is TaskStatus.PENDING:
                task.scope.cancel()

    def _execute_tasks_modal(
        self,
        session: ExecutionSession,
        execution: ExecutionTarget,
        job: Job,
    ) -> Iterator[TaskProgress]:
        self.before_job_tasks(session)
        with job.scene_prepare as bake_objects:
            session.bake_objects = bake_objects

            for index, task in enumerate(job.tasks):
                if type(task).__name__ not in self.task_type_names:
                    continue

                if self._cancel_requested or session.is_cancelled or job.scope.is_cancelled:
                    raise TaskCancelled(f"Job '{job.uuid}' was cancelled")

                task_executor = registry_executor[task.id]
                session.current_task = task
                with task.scope:
                    result_scope = task_executor.execute_task(
                        session=session,
                        execution=execution,
                        task=task,
                    )
                    LOG.info(
                        f"Task ended with {result_scope.status.name.capitalize()} "
                        f"in {result_scope.duration:.2f}s",
                        display_in_ui=True,
                    )

                # Yield only after task.scope and all scopes created inside
                # execute_task have exited. Never suspend the generator while
                # the synchronous scope stack contains a task scope.
                yield TaskProgress(
                    message=f"Completed {index + 1} / {job.total_tasks}: {task.name}"
                )

        self.after_job_tasks(session)

    def _execute_tasks_sync(self, session: ExecutionSession, execution: ExecutionTarget, job: Job):
        self.before_job(session)
        try:
            with job.scene_prepare as bake_objects:
                session.bake_objects = bake_objects
                for task in job.tasks:
                    if type(task).__name__ not in self.task_type_names:
                        continue
                    if self._cancel_requested:
                        session.cancel()
                        job.cancel()
                        break
                    task_executor = registry_executor[task.id]
                    session.current_task = task
                    with task.scope:
                        result_scope = task_executor.execute_task(
                            session=session,
                            execution=execution,
                            task=task,
                        )
                        LOG.info(
                            f"Task ended with {result_scope.status.name.capitalize()} "
                            f"in {result_scope.duration:.2f}s",
                            display_in_ui=True,
                        )
            self.after_job(session)
        except KeyboardInterrupt:
            LOG.warning("Job interrupted")
            session.cancel()
            job.cancel()
        except Exception as exc:
            traceback.print_exc()
            job.status = JobStatus.FAILED
            job.notify_failed(perf_counter() - self.start, str(exc))

    def finish(
        self,
        session: ExecutionSession,
        context: bpy.types.Context,
        job: Job,
        *,
        restore: bool = True,
    ):
        """Release session resources and restore Blender state when captured."""
        try:
            session.cleanup()
        finally:
            try:
                if restore:
                    session.restore(context)
            finally:
                try:
                    session.dispose()
                finally:
                    job.notify_finished()

    def before_job(self, session: ExecutionSession) -> None:
        pass

    def after_job(self, session: ExecutionSession) -> None:
        pass

    def before_job_tasks(self, session: ExecutionSession) -> None:
        pass

    def after_job_tasks(self, session: ExecutionSession) -> None:
        pass

    def before_task(self, ctx: ExecutionContext) -> None:
        pass

    def after_task(self, ctx: ExecutionContext) -> None:
        pass

    def cancel(self) -> None:
        self._cancel_requested = True
        if self._modal_runner is not None:
            self._modal_runner.cancel()

    @property
    def cancelled(self) -> bool:
        return self._cancel_requested or bool(
            self._modal_runner is not None and self._modal_runner.scope.is_cancelled
        )
