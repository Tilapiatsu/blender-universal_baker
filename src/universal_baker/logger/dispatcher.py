from __future__ import annotations

from .event import LogEvent
from .sinks.base import BaseSink


class Dispatcher:
    def __init__(self) -> None:
        self._sinks: dict[str, BaseSink] = {}

    def get(self, name: str) -> BaseSink | None:
        return self._sinks.get(name)

    def add_sink(self, name: str, sink: BaseSink) -> None:
        self._sinks[name] = sink

    def remove_sink(self, name: str) -> None:
        if name in self._sinks:
            del self._sinks[name]

    def dispatch(self, event: LogEvent) -> None:
        for sink in self._sinks.values():
            if sink.accepts(event):
                sink.write(event)

    def close(self):
        for sink in self._sinks.values():
            sink.close()
