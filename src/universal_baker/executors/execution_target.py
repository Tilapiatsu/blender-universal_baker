from __future__ import annotations

from abc import ABC

from ..enum.execution import Execution
from ..runtime.session import ExecutionSession
from ..runtime.context import ExecutionContext


class ExecutionTarget(ABC):
    execution: Execution

    def execute(
        self,
        session: ExecutionSession,
        task,
        context: ExecutionContext,
    ) -> None: ...
