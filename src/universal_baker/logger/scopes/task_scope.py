from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

from .task_status import TaskStatus


@dataclass(slots=True)
class TaskScope:
    id: int
    name: str
    manager: Any
    parent: TaskScope | None = None
    weight: float = 1.0
    status: TaskStatus = TaskStatus.PENDING
    _progress: float = 0.0
    start_time: float | None = None
    end_time: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    children: list[TaskScope] = field(default_factory=list)
    error: BaseException | None = None
    detached: bool = False
    cancellation_requested: bool = False

    @property
    def progress(self) -> float:
        if not self.children:
            return self._progress
        total = sum(child.weight for child in self.children)
        if total <= 0:
            return 0.0
        return sum(child.weight * child.progress for child in self.children) / total

    def set_progress(self, value: float):
        if self.children:
            raise RuntimeError("Progress is derived from children for this scope")
        if self.status is not TaskStatus.RUNNING:
            raise RuntimeError("Progress can only be updated while a scope is running")
        self._progress = max(0.0, min(1.0, float(value)))
        self.manager.notify_update(self)

    @property
    def duration(self) -> float | None:
        if self.start_time is None:
            return None
        return (self.end_time or time.perf_counter()) - self.start_time

    @property
    def path(self) -> tuple[str, ...]:
        return (self.name,) if self.parent is None else (*self.parent.path, self.name)

    def create_child(self, name: str, weight: float = 1.0, **metadata) -> TaskScope:
        return self.manager.create_scope(name, parent=self, weight=weight, **metadata)

    def bind(self):
        return self.manager.bind(self)

    def set_warning(self):
        self.manager.set_status(self, TaskStatus.WARNING)

    def cancel(self):
        """Mark the scope cancelled (for synchronous/cooperative callers)."""
        self.cancellation_requested = True
        if self.status in (TaskStatus.PENDING, TaskStatus.RUNNING):
            self.manager.set_status(self, TaskStatus.CANCELLED)

    def request_cancel(self):
        """Request cancellation without prematurely ending the scope."""
        self.cancellation_requested = True
        self.manager.notify_update(self)

    @property
    def is_cancelled(self) -> bool:
        return self.cancellation_requested or self.status is TaskStatus.CANCELLED

    def raise_if_cancelled(self):
        if self.is_cancelled:
            raise TaskCancelled(f"Task '{self.name}' was cancelled")

    def set_error(self, error: BaseException | None = None):
        self.error = error
        self.manager.set_status(self, TaskStatus.ERROR)

    def __enter__(self):
        self.manager.enter(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.manager.exit(self, exc_value)
        return False


class TaskCancelled(Exception):
    """Cooperative task cancellation signal."""
