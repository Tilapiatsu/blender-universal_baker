from __future__ import annotations

import time
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

    # ---------------------------------------------------------
    # Progress
    # ---------------------------------------------------------

    @property
    def progress(self) -> float:
        """
        Return weighted child progress when children exist.
        Otherwise return manually assigned progress.
        """

        if not self.children:
            return self._progress

        total_weight = sum(child.weight for child in self.children)

        if total_weight <= 0:
            return 0.0

        completed_weight = sum(child.weight * child.progress for child in self.children)

        return completed_weight / total_weight

    def set_progress(self, value: float):
        if self.children:
            raise RuntimeError("Progress is derived from children for this scope")

        self._progress = max(0.0, min(1.0, float(value)))
        self.manager.notify_update(self)

    # ---------------------------------------------------------
    # Timing
    # ---------------------------------------------------------

    @property
    def duration(self) -> float | None:
        if self.start_time is None:
            return None

        end = self.end_time

        if end is None:
            end = time.perf_counter()

        return end - self.start_time

    # ---------------------------------------------------------
    # Hierarchy
    # ---------------------------------------------------------

    @property
    def path(self) -> tuple[str, ...]:
        if self.parent is None:
            return (self.name,)

        return (*self.parent.path, self.name)

    def create_child(
        self,
        name: str,
        weight: float = 1.0,
        **metadata,
    ) -> TaskScope:
        return self.manager.create_scope(
            name=name,
            parent=self,
            weight=weight,
            **metadata,
        )

    # ---------------------------------------------------------
    # Status
    # ---------------------------------------------------------

    def set_warning(self):
        self.manager.set_status(self, TaskStatus.WARNING)

    def cancel(self):
        self.manager.set_status(self, TaskStatus.CANCELLED)

    def set_error(self, error: BaseException | None = None):
        self.error = error
        self.manager.set_status(self, TaskStatus.ERROR)

    # ---------------------------------------------------------
    # Context manager
    # ---------------------------------------------------------

    def __enter__(self):
        self.manager.enter(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.manager.exit(self, exc_value)

        # Never swallow exceptions.
        return False
