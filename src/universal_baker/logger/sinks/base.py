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

    def close(self):
        pass

    def prettify_severity(self, level: Severity) -> str:
        severity = level.name

        if len(severity) == 4:
            severity = f"  {severity}  "
        elif len(severity) == 5:
            severity = f" {severity}  "
        elif len(severity) == 7:
            severity = f" {severity}"

        return severity
