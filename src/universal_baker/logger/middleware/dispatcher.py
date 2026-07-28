from __future__ import annotations

from collections import OrderedDict
from ..event import LogEvent
from .base import BaseMiddleware


class MiddlewareDispatcher:
    def __init__(self):
        self._middleware = OrderedDict()

    @property
    def ordered_middleware(self):
        middleware = list(self._middleware.values())
        middleware.sort(key=lambda m: m.priority)
        return middleware

    def add(self, middleware, name=None):
        name = name or middleware.__class__.__name__
        self._middleware[name] = middleware

    def remove(self, name: str):
        try:
            self._middleware.pop(name)
        except KeyError:
            print(f"Middleware {name} not found")

    def get(self, name: str) -> BaseMiddleware | None:
        return self._middleware[name]

    def process(self, event: LogEvent) -> LogEvent | None:
        for middleware in self.ordered_middleware:
            event = middleware.process(event)

            if event is None:
                return None

        return event
