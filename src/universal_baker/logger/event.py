from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from .scopes.task_status import ScopeState, TaskStatus
from .severity import Severity


@dataclass(slots=True, frozen=True)
class LogEvent:
    severity: Severity
    message: str

    scope: tuple[str, ...] = field(default_factory=tuple)
    scope_id: int | None = None
    parent_scope_id: int | None = None

    display_in_ui: bool = False
    ui_channel: str | None = None

    scope_state: ScopeState | None = None
    task_status: TaskStatus | None = None

    progress: float | None = None
    scope_duration: float | None = None
    scope_metadata: dict[str, Any] = field(default_factory=dict)

    timestamp: float = field(default_factory=time.time)
    addon: str | None = None
    category: str | None = None

    # The exception is retained for consumers that need the original object.
    # traceback_text is captured at log time so the UI does not need to retain
    # or inspect traceback frames when drawing.
    exception: Exception | None = None
    traceback_text: str | None = None

    data: dict[str, Any] = field(default_factory=dict)
