from abc import ABC, abstractmethod

from ..event import LogEvent
from ..severity import Severity


class BaseSink(ABC):
    def __init__(self, level: Severity = Severity.INFO):
        self.level = level

    def accepts(self, event: LogEvent) -> bool:
        return event.severity >= self.level

    @abstractmethod
    def write(self, event: LogEvent):
        pass
