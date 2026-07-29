from __future__ import annotations
from enum import Enum, auto

from ..logger.middleware.base import BaseMiddleware
from ..logger.event import LogEvent


class BakeStatus(Enum):
    SUCCESS = auto()
    FAIL = auto()


class EventCategory(Enum):
    BAKE = auto()
    PACK = auto()


class BakeSummaryMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.clear()

    def clear(self):
        self.successes = []
        self.failures = []

    def process(self, event) -> LogEvent:

        if event.category not in [EventCategory.BAKE, EventCategory.PACK]:
            return event

        status = event.data.get("status")

        if status == BakeStatus.SUCCESS:
            self.successes.append(event)

        elif status == BakeStatus.FAIL:
            self.failures.append(event)

        return event
