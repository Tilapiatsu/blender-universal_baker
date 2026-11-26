from __future__ import annotations

import contextvars
import time
from contextlib import contextmanager
from itertools import count

from .task_scope import TaskCancelled, TaskScope
from .task_status import ScopeState, TaskStatus


class ScopeManager:
    """Owns scope trees and context-local synchronous scope bindings.

    Detached scopes are ordinary scope-tree roots (or explicitly parented
    scopes) that do not become the current scope until temporarily bound.
    ContextVar keeps bindings isolated between independent execution contexts.
    """

    def __init__(self, emit_callback):
        self._emit_callback = emit_callback
        self._current_stack = contextvars.ContextVar(f"logger_scope_stack_{id(self)}", default=())
        self._roots: list[TaskScope] = []
        self._ids = count(1)

    @property
    def _stack(self):
        """Compatibility/read-only view of the current context's stack."""
        return self._current_stack.get()

    @property
    def current(self) -> TaskScope | None:
        stack = self._current_stack.get()
        return stack[-1] if stack else None

    @property
    def current_path(self) -> tuple[str, ...]:
        current = self.current
        return current.path if current else ()

    @property
    def roots(self) -> tuple[TaskScope, ...]:
        return tuple(self._roots)

    def create_scope(
        self,
        name: str,
        parent: TaskScope | None = None,
        weight: float = 1.0,
        detached: bool = False,
        **metadata,
    ) -> TaskScope:
        if weight <= 0:
            raise ValueError("Scope weight must be greater than zero")
        if detached and parent is None:
            parent = None
        elif parent is None:
            parent = self.current

        scope = TaskScope(
            id=next(self._ids),
            name=name,
            manager=self,
            parent=parent,
            weight=weight,
            metadata=metadata,
            detached=detached,
        )
        if parent is not None:
            parent.children.append(scope)
        else:
            self._roots.append(scope)
        self._emit(scope, ScopeState.CREATE)
        if parent is not None:
            self.notify_update(parent)
        return scope

    def enter(self, scope: TaskScope):
        if scope.status is not TaskStatus.PENDING:
            raise RuntimeError(f"Cannot enter scope '{scope.name}' with status {scope.status.name}")
        stack = self._current_stack.get()
        if scope.parent is not None and scope.parent is not (stack[-1] if stack else None):
            raise RuntimeError(f"Scope '{scope.name}' must be entered while its parent is active")
        if scope in stack:
            raise RuntimeError("Scope is already active")
        scope.status = TaskStatus.RUNNING
        scope.start_time = time.perf_counter()
        self._current_stack.set((*stack, scope))
        self._emit(scope, ScopeState.ENTER)
        self._notify_parent(scope)

    def exit(self, scope: TaskScope, error=None):
        stack = self._current_stack.get()
        if not stack or stack[-1] is not scope:
            raise RuntimeError(f"Scope stack mismatch while exiting '{scope.name}'")
        if isinstance(error, TaskCancelled):
            scope.cancellation_requested = True
            scope.status = TaskStatus.CANCELLED
        elif error is not None:
            scope.error = error
            scope.status = TaskStatus.ERROR
        elif scope.status is TaskStatus.RUNNING:
            scope.status = TaskStatus.SUCCESS
        scope.end_time = time.perf_counter()
        if scope.status is TaskStatus.SUCCESS:
            scope._progress = 1.0
        self._current_stack.set(stack[:-1])
        self._emit(scope, ScopeState.EXIT)
        self._notify_parent(scope)

    def start_detached(self, scope: TaskScope):
        """Start a detached root scope without retaining a context-local stack entry.

        Modal operations span multiple Blender event callbacks. A ContextVar
        binding must never be left open across those callbacks, so their root
        lifecycle is managed independently from temporary log attribution.
        """
        if not scope.detached or scope.parent is not None:
            raise RuntimeError("A modal lifecycle requires a detached root scope")
        if scope.status is not TaskStatus.PENDING:
            raise RuntimeError(f"Cannot start detached scope '{scope.name}' with status {scope.status.name}")
        scope.status = TaskStatus.RUNNING
        scope.start_time = time.perf_counter()
        self._emit(scope, ScopeState.ENTER)
        self._notify_parent(scope)

    def finish_detached(self, scope: TaskScope, error=None, *, cancelled=False):
        """Finish a detached root scope without touching the current stack."""
        if not scope.detached or scope.parent is not None:
            raise RuntimeError("A modal lifecycle requires a detached root scope")
        if scope.status is not TaskStatus.RUNNING:
            # Make repeated cleanup harmless, but reject an unrelated pending
            # or already-terminal scope rather than silently corrupting it.
            if scope.end_time is not None:
                return
            raise RuntimeError(f"Cannot finish detached scope '{scope.name}' with status {scope.status.name}")
        if error is not None:
            scope.error = error
            scope.status = TaskStatus.ERROR
        elif cancelled:
            scope.cancellation_requested = True
            scope.status = TaskStatus.CANCELLED
        else:
            scope.status = TaskStatus.SUCCESS
            scope._progress = 1.0
        scope.end_time = time.perf_counter()
        self._emit(scope, ScopeState.EXIT)
        self._notify_parent(scope)

    @contextmanager
    def bind(self, scope: TaskScope):
        """Temporarily make an already-created scope the current scope.

        Binding does not enter/exit or alter lifecycle state. It is intended
        for logging from callbacks that belong to a detached operation.
        """
        stack = self._current_stack.get()
        if scope.status is not TaskStatus.RUNNING:
            raise RuntimeError("Only a running scope can be bound")
        if scope.parent is not None and scope.parent not in stack:
            raise RuntimeError("A child scope can only be bound while its parent is active")
        token = self._current_stack.set((*stack, scope))
        try:
            yield scope
        finally:
            self._current_stack.reset(token)

    def set_status(self, scope: TaskScope, status: TaskStatus):
        if scope.status not in (TaskStatus.PENDING, TaskStatus.RUNNING):
            raise RuntimeError(f"Cannot change completed scope '{scope.name}'")
        scope.status = status
        self.notify_update(scope)

    def notify_update(self, scope: TaskScope):
        self._emit(scope, ScopeState.UPDATE)
        self._notify_parent(scope)

    def _notify_parent(self, scope: TaskScope):
        if scope.parent is not None:
            self.notify_update(scope.parent)

    def _emit(self, scope: TaskScope, state: ScopeState):
        self._emit_callback(scope=scope, state=state)
