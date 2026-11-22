from __future__ import annotations

from enum import Enum, auto


class TaskStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    WARNING = auto()
    ERROR = auto()
    CANCELLED = auto()


class ScopeState(Enum):
    ENTER = auto()
    UPDATE = auto()
    EXIT = auto()
