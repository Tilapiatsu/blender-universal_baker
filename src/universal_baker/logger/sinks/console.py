from datetime import datetime

from .base import BaseSink
from ..event import LogEvent


class ConsoleSink(BaseSink):
    def write(self, event: LogEvent):
        timestamp = datetime.fromtimestamp(event.timestamp).strftime("%H:%M:%S")

        print(f"[{timestamp}] [{event.severity.name}] {event.message}")
