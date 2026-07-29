from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from enum import Enum, auto
import time

from .severity import Severity


class ScopeState(Enum):
    ENTER = auto()
    EXIT = auto()
    UPDATE = auto()


@dataclass(slots=True, frozen=True)
class LogEvent:
    severity: Severity
    message: str
    scope: tuple[str, ...]
    scope_state: ScopeState | None = None
    scope_duration: float | None = None
    progress: float | None = None
    timestamp: float = field(default_factory=time.time)
    addon: str | None = None
    category: str | None = None
    exception: Exception | None = None
    data: dict[str, Any] = field(default_factory=dict)
    scope: tuple[str, ...] = field(default_factory=tuple)
