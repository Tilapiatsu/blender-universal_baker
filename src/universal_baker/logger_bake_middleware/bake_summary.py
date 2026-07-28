from __future__ import annotations

from ..logger.middleware.base import BaseMiddleware
from ..logger.event import LogEvent


class BakeSummaryMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.successes = []
        self.failures = []

    def process(self, event) -> LogEvent:

        if event.category not in ["BAKE", "PACK"]:
            return event

        status = event.data.get("status")

        if status == "SUCCESS":
            self.successes.append(event)

        elif status == "FAILED":
            self.failures.append(event)

        return event
