from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import time


@dataclass(slots=True)
class TaskScope:
    name: str
    parent: TaskScope | None = None
    start_time: float = field(default_factory=time.perf_counter)
    end_time: float | None = None
    progress: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    children: list[TaskScope] = field(default_factory=list)

    @property
    def duration(self) -> float | None:
        if self.end_time is None:
            return None

        return self.end_time - self.start_time

    @property
    def is_finished(self) -> bool:
        return self.end_time is not None

    def finish(self):
        if self.end_time is None:
            self.end_time = time.perf_counter()

    def set_progress(self, value: float):
        self.progress = max(0.0, min(1.0, value))

    def add_child(self, child: TaskScope):
        child.parent = self
        self.children.append(child)
