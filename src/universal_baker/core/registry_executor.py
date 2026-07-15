from __future__ import annotations

from typing import Dict

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..executors.executor_base import TaskExecutor


class ExecutorRegistry:
    def __init__(self):
        self._executor: Dict[str, TaskExecutor] = {}

    def register(self, executor: TaskExecutor) -> None:
        if executor.id in self._executor:
            raise ValueError(f"Executor '{executor.id}' already registered.")

        self._executor[executor.id] = executor

    def unregister(self, executor_id: str) -> None:
        self._executor.pop(executor_id, None)

    def __getitem__(self, executor_id: str) -> TaskExecutor:
        return self._executor[executor_id]

    def exists(self, executor_id: str) -> bool:
        return executor_id in self._executor

    def items(self):
        return self._executor.items()

    def values(self):
        return self._executor.values()

    def keys(self):
        return self._executor.keys()


registry_executor = ExecutorRegistry()
