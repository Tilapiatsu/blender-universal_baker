from __future__ import annotations

from .base import BaseMiddleware
from ..severity import Severity
from ..event import LogEvent


class IgnoreDebugMiddleware(BaseMiddleware):
    def process(self, event: LogEvent) -> LogEvent | None:

        if event.severity == Severity.DEBUG:
            return None

        return event
