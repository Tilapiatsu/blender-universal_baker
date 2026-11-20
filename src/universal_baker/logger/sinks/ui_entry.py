from __future__ import annotations

from dataclasses import dataclass

from ..event import LogEvent
from ..scopes.task_scope import TaskScope


@dataclass(slots=True)
class UIEntry:
    id: int
    scope: TaskScope | None = None
    event: LogEvent | None = None

    expanded: bool = True
    visible: bool = True
