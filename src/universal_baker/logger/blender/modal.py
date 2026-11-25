from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from itertools import count
from typing import Any

import bpy

from ..scopes.task_scope import TaskCancelled, TaskScope
from ..scopes.task_status import TaskStatus


@dataclass(slots=True, frozen=True)
class TaskProgress:
    """Optional value yielded by a modal task to update its scope/UI."""

    progress: float | None = None
    message: str | None = None


_ACTIVE_RUNNERS: dict[str, ModalTaskRunner] = {}
_RUNNER_IDS = count(1)


class LOGGER_OT_RunModalTask(bpy.types.Operator):
    bl_idname = "logger.run_modal_task"
    bl_label = "Run Logger Task"
    bl_options = {"INTERNAL"}

    runner_key: bpy.props.StringProperty(options={"HIDDEN"})

    def invoke(self, context, event):
        runner = _ACTIVE_RUNNERS.get(self.runner_key)
        if runner is None:
            return {"CANCELLED"}
        if context.window is None:
            runner._finish(error=RuntimeError("A Blender window is required for modal execution"))
            return {"CANCELLED"}
        self._runner = runner
        self._timer = context.window_manager.event_timer_add(runner.interval, window=context.window)
        runner._operator = self
        runner._window_manager = context.window_manager
        runner._timer_handle = self._timer
        try:
            runner._start_scope()
            context.window_manager.modal_handler_add(self)
        except BaseException as exc:
            runner._finish(error=exc)
            return {"CANCELLED"}
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        runner = self._runner
        if runner._finished:
            return {"FINISHED"}

        if event.type in {"ESC", "RIGHTMOUSE"} and event.value == "PRESS":
            runner.cancel()
            return {"CANCELLED"}

        if event.type == "TIMER":
            try:
                runner._advance()
            except StopIteration:
                runner._finish()
                return {"FINISHED"}
            except TaskCancelled:
                runner._finish(cancelled=True)
                return {"CANCELLED"}
            except BaseException as exc:
                runner._finish(error=exc)
                return {"CANCELLED"}

        return {"RUNNING_MODAL"}

    def cancel(self, context):
        if hasattr(self, "_runner"):
            self._runner.cancel()


class ModalTaskRunner:
    """Run a generator/iterator incrementally through Blender modal TIMER events.

    The iterator must yield control regularly. Each TIMER event advances at
    most ``steps_per_tick`` yields, allowing Blender to process redraws and
    input between batches. Yield TaskProgress(...) to report progress.
    """

    def __init__(
        self,
        logger,
        *,
        interval: float = 0.05,
        steps_per_tick: int = 1,
        on_complete: Callable[[Any], None] | None = None,
        on_cancel: Callable[[], None] | None = None,
        on_error: Callable[[BaseException], None] | None = None,
    ):
        if interval <= 0:
            raise ValueError("interval must be greater than zero")
        if steps_per_tick < 1:
            raise ValueError("steps_per_tick must be at least one")
        self.logger = logger
        self.interval = float(interval)
        self.steps_per_tick = int(steps_per_tick)
        self.on_complete = on_complete
        self.on_cancel = on_cancel
        self.on_error = on_error
        self._finished = True
        self._scope_entered = False

    def start(self, context, task, *, scope: TaskScope | None = None):
        """Start ``task`` (a generator or iterator) as a modal operation."""
        if not self._finished:
            raise RuntimeError("This ModalTaskRunner is already running")
        self._iterator = iter(task)
        if not hasattr(self._iterator, "__next__"):
            raise TypeError("task must be an iterable or iterator")
        self.scope = scope or self.logger.detached_scope(getattr(task, "__name__", "Background task"))
        if self.scope.status is not TaskStatus.PENDING:
            raise RuntimeError("The supplied task scope must be pending")
        self._key = str(next(_RUNNER_IDS))
        self._finished = False
        self._result = None
        self._operator = None
        self._window_manager = None
        self._timer_handle = None
        _ACTIVE_RUNNERS[self._key] = self
        try:
            result = bpy.ops.logger.run_modal_task("INVOKE_DEFAULT", runner_key=self._key)
            if "CANCELLED" in result and not self._finished:
                self._finish(error=RuntimeError("Blender refused to start the modal task"))
        except BaseException:
            _ACTIVE_RUNNERS.pop(self._key, None)
            self._finished = True
            raise
        return self

    def cancel(self):
        if self._finished:
            return
        self.scope.request_cancel()
        self._finish(cancelled=True)

    def _start_scope(self):
        self.logger.scope_manager.enter(self.scope)
        self._scope_entered = True

    def _advance(self):
        self.scope.raise_if_cancelled()
        for _ in range(self.steps_per_tick):
            try:
                with self.logger.bind_scope(self.scope):
                    yielded = next(self._iterator)
            except StopIteration as stop:
                self._result = stop.value
                raise
            if isinstance(yielded, TaskProgress):
                with self.logger.bind_scope(self.scope):
                    if yielded.message:
                        self.logger.info(yielded.message, display_in_ui=True)
                    if yielded.progress is not None:
                        self.scope.set_progress(yielded.progress)
            elif isinstance(yielded, (int, float)):
                with self.logger.bind_scope(self.scope):
                    self.scope.set_progress(float(yielded))
        # Refresh elapsed duration even when no explicit progress was yielded.
        self.scope.manager.notify_update(self.scope)

    def _finish(self, *, error=None, cancelled=False):
        if self._finished:
            return
        self._finished = True
        _ACTIVE_RUNNERS.pop(getattr(self, "_key", ""), None)
        try:
            if error is not None and getattr(self, "_scope_entered", False):
                # Attach the failure message to the task before it becomes terminal.
                with self.logger.bind_scope(self.scope):
                    self.logger.error(
                        f"Task failed: {error}",
                        exception=error,
                        display_in_ui=True,
                    )
            if cancelled:
                self.scope.cancellation_requested = True
                if self.scope.status in (TaskStatus.PENDING, TaskStatus.RUNNING):
                    self.scope.status = TaskStatus.CANCELLED
            elif error is not None:
                self.scope.error = error
                if self.scope.status in (TaskStatus.PENDING, TaskStatus.RUNNING):
                    self.scope.status = TaskStatus.ERROR
            if getattr(self, "_scope_entered", False):
                # exit() preserves ERROR/CANCELLED and closes duration/stack.
                self.logger.scope_manager.exit(self.scope, error if error is not None else None)
                self._scope_entered = False
            elif self.scope.status is TaskStatus.PENDING:
                # Startup failed before entering the scope; still make the
                # lifecycle visible and terminal rather than leaving a ghost.
                self.logger.scope_manager.enter(self.scope)
                self.logger.scope_manager.exit(self.scope, error)
        finally:
            wm = getattr(self, "_window_manager", None)
            timer = getattr(self, "_timer_handle", None)
            if wm is not None and timer is not None:
                try:
                    wm.event_timer_remove(timer)
                except (ReferenceError, RuntimeError):
                    pass
            self._timer_handle = None
            self._operator = None

        try:
            if error is not None:
                if self.on_error:
                    self.on_error(error)
            elif cancelled:
                if self.on_cancel:
                    self.on_cancel()
            elif self.on_complete:
                self.on_complete(self._result)
        except BaseException as callback_error:
            # Callback failures are reported but cannot undo task cleanup.
            self.logger.error(
                f"Task completion callback failed: {callback_error}",
                exception=callback_error,
                display_in_ui=True,
            )


def cancel_all_modal_tasks():
    """Cancel active runners before unregistering the Blender operators."""
    for runner in tuple(_ACTIVE_RUNNERS.values()):
        runner.cancel()
