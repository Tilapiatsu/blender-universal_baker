from __future__ import annotations

from dataclasses import dataclass

from .session import ExecutionSession


@dataclass(slots=True)
class ExecutionContext:
    session: ExecutionSession

    def __init__(self, session: ExecutionSession) -> None:
        self.session = session
