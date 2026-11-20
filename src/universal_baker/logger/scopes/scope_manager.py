from __future__ import annotations

import time
from itertools import count

from .task_scope import TaskScope
from .task_status import ScopeState, TaskStatus


class ScopeManager:
    def __init__(self, emit_callback):
        self._emit_callback = emit_callback
        self._stack: list[TaskScope] = []
        self._roots: list[TaskScope] = []
        self._ids = count(1)

    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------

    @property
    def current(self) -> TaskScope | None:
        return self._stack[-1] if self._stack else None

    @property
    def current_path(self) -> tuple[str, ...]:
        current = self.current
        return current.path if current else ()

    @property
    def roots(self) -> tuple[TaskScope, ...]:
        return tuple(self._roots)

    # ---------------------------------------------------------
    # Creation
    # ---------------------------------------------------------

    def create_scope(
        self,
        name: str,
        parent: TaskScope | None = None,
        weight: float = 1.0,
        **metadata,
    ) -> TaskScope:

        if weight <= 0:
            raise ValueError("Scope weight must be greater than zero")

        if parent is None:
            parent = self.current

        scope = TaskScope(
            id=next(self._ids),
            name=name,
            manager=self,
            parent=parent,
            weight=weight,
            metadata=metadata,
        )

        if parent is not None:
            parent.children.append(scope)
        else:
            self._roots.append(scope)

        if parent is not None:
            self.notify_update(parent)

        return scope

    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------

    def enter(self, scope: TaskScope):
        if scope.status is not TaskStatus.PENDING:
            raise RuntimeError(f"Cannot enter scope '{scope.name}' with status {scope.status.name}")

        if scope.parent is not self.current and scope.parent is not None:
            raise RuntimeError(f"Scope '{scope.name}' must be entered while its parent is active")

        if scope in self._stack:
            raise RuntimeError("Scope is already active")

        scope.status = TaskStatus.RUNNING
        scope.start_time = time.perf_counter()

        self._stack.append(scope)

        self._emit(scope, ScopeState.ENTER)
        self._notify_parent(scope)

    def exit(self, scope: TaskScope, error=None):
        if not self._stack or self._stack[-1] is not scope:
            raise RuntimeError(f"Scope stack mismatch while exiting '{scope.name}'")

        if error is not None:
            scope.error = error
            scope.status = TaskStatus.ERROR

        elif scope.status is TaskStatus.RUNNING:
            scope.status = TaskStatus.SUCCESS

        scope.end_time = time.perf_counter()

        if scope.status is TaskStatus.SUCCESS:
            scope._progress = 1.0

        self._stack.pop()

        self._emit(scope, ScopeState.EXIT)
        self._notify_parent(scope)

    # ---------------------------------------------------------
    # Updates
    # ---------------------------------------------------------

    def set_status(self, scope: TaskScope, status: TaskStatus):
        if scope.status not in (
            TaskStatus.PENDING,
            TaskStatus.RUNNING,
        ):
            raise RuntimeError(f"Cannot change completed scope '{scope.name}'")

        scope.status = status
        self.notify_update(scope)

    def notify_update(self, scope: TaskScope):
        self._emit(scope, ScopeState.UPDATE)
        self._notify_parent(scope)

    def _notify_parent(self, scope: TaskScope):
        if scope.parent is not None:
            self.notify_update(scope.parent)

    # ---------------------------------------------------------
    # Event dispatch
    # ---------------------------------------------------------

    def _emit(self, scope: TaskScope, state: ScopeState):
        self._emit_callback(
            scope=scope,
            state=state,
        )
