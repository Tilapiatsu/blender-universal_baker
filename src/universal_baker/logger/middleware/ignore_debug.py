from __future__ import annotations

from ..event import LogEvent
from ..severity import Severity
from .base import BaseMiddleware


class IgnoreDebugMiddleware(BaseMiddleware):
    def process(self, event: LogEvent) -> LogEvent | None:

        if event.severity == Severity.DEBUG:
            return None

        return event
