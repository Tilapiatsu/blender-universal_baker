from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..executors.executor_base import TaskExecutor


class ExecutorRegistry:
    def __init__(self):
        self._executors: Dict[str, TaskExecutor] = {}

    def register(self, executor: TaskExecutor) -> None:
        if executor.id in self._executors:
            raise ValueError(f"Executor '{executor.id}' already registered.")

        self._executors[executor.id] = executor

    def unregister(self, executor_id: str) -> None:
        if executor_id not in self._executors:
            return

        self._executors.pop(executor_id, None)

    def __getitem__(self, executor_id: str) -> TaskExecutor:
        return self._executors[executor_id]

    def exists(self, executor_id: str) -> bool:
        return executor_id in self._executors

    def items(self):
        return self._executors.items()

    def values(self):
        return self._executors.values()

    def keys(self):
        return self._executors.keys()


registry_executor = ExecutorRegistry()
