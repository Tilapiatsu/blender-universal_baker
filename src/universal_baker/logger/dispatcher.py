from .event import LogEvent
from .sinks.base import BaseSink


class Dispatcher:
    def __init__(self):
        self._sinks = []

    def add_sink(self, sink: BaseSink):
        self._sinks.append(sink)

    def remove_sink(self, sink: BaseSink):
        self._sinks.remove(sink)

    def dispatch(self, event: LogEvent):
        for sink in self._sinks:
            if sink.accepts(event):
                sink.write(event)
