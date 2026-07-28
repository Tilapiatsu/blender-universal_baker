from abc import ABC, abstractmethod

from ..event import LogEvent


class BaseMiddleware(ABC):
    priority: int = 100

    @abstractmethod
    def process(self, event: LogEvent) -> LogEvent | None:
        """
        Process an event.

        Return:
            LogEvent -> continue processing
            None     -> stop propagation
        """
        raise NotImplementedError
