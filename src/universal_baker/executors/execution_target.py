from __future__ import annotations

from abc import ABC

from ..enum.execution import Execution
from ..logger.event import ScopeState
from ..logger_bake_middleware.bake_summary import EventCategory
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
