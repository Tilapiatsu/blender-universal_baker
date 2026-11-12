from __future__ import annotations

from abc import ABC

from ..enum.execution import Execution
from ..runtime.context import ExecutionContext
from ..runtime.session import ExecutionSession


class ExecutionTarget(ABC):
    execution: Execution

    def execute(
        self,
        session: ExecutionSession,
        task,
        context: ExecutionContext,
    ) -> None: ...
