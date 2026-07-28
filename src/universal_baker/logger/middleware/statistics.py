from __future__ import annotations

from .base import BaseMiddleware
from ..severity import Severity


class StatisticsMiddleware(BaseMiddleware):
    def __init__(self):
        self.total = 0
        self.info = 0
        self.warning = 0
        self.error = 0
        self.debug = 0

    def process(self, event):
        self.total += 1

        match event.severity:
            case Severity.INFO:
                self.info += 1
            case Severity.WARNING:
                self.warning += 1
            case Severity.ERROR:
                self.error += 1
            case Severity.DEBUG:
                self.debug += 1

        return event
