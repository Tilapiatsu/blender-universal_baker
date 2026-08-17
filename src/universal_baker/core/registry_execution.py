from __future__ import annotations

from typing import Dict

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..executors.execution_target import ExecutionTarget
    from ..enum.execution import Execution


class ExecutionRegistry:
    def __init__(self):
        self._executions: Dict[Execution, ExecutionTarget] = {}

    def register(self, execution: ExecutionTarget) -> None:
        if execution.execution in self._executions:
            raise ValueError(f"Compositor '{execution.execution.value}' already registered.")

        self._executions[execution.execution] = execution

    def unregister(self, execution: Execution) -> None:
        self._executions.pop(execution, None)

    def __getitem__(self, execution: Execution) -> ExecutionTarget:
        return self._executions[execution]

    def exists(self, execution: Execution) -> bool:
        return execution in self._executions

    def items(self):
        return self._executions.items()

    def values(self):
        return self._executions.values()

    def keys(self):
        return self._executions.keys()


registry_execution = ExecutionRegistry()
