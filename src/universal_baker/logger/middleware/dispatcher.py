from ..event import LogEvent
from collections import OrderedDict


class MiddlewareDispatcher:
    def __init__(self):
        self._middleware = OrderedDict()

    def add(self, middleware, name=None):
        name = name or middleware.__class__.__name__
        self._middleware[name] = middleware

    def remove(self, name: str):
        del self._middleware[name]

    def process(self, event: LogEvent) -> LogEvent | None:

        for middleware in self._middleware:
            event = middleware.process(event)

            if event is None:
                return None

        return event
