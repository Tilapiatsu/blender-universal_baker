from __future__ import annotations

from enum import Enum, StrEnum, auto

from ..logger.event import LogEvent
from ..logger.middleware.base import BaseMiddleware


class BakeStatus(Enum):
    SUCCESS = auto()
    FAIL = auto()


class EventCategory(StrEnum):
    INIT = "INIT"
    EVALUATE_MESHES = "EVALUATE_MESHES"
    OWNERSHIP = "OWNERSHIP"
    BAKE = "BAKE"
    PACK = "PACK"
    ACCUMULATE = "ACCUMULATE"
    MASK = "MASK"


class BakeSummaryMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.clear()

    def clear(self):
        self.successes = []
        self.failures = []

    def process(self, event) -> LogEvent:

        if event.category not in [EventCategory.BAKE, EventCategory.PACK, EventCategory.ACCUMULATE]:
            return event

        status = event.data.get("status")

        if status == BakeStatus.SUCCESS:
            self.successes.append(event)

        elif status == BakeStatus.FAIL:
            self.failures.append(event)

        return event
