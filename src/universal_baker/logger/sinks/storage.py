from __future__ import annotations

from collections import deque
from collections.abc import Iterator

from .base import BaseSink
from .storage_entry import StoredEvent
from ..event import LogEvent
from ..severity import Severity


class StorageSink(BaseSink):
    """
    Sink storing log events in memory.

    This class is the base for every stateful sink such as:

        - UISink
        - ViewportSink

    It provides event storage, iteration, filtering and memory limits.
    """

    def __init__(self, level: Severity = Severity.INFO, max_events: int = 500):

        super().__init__(level)
        self._events: deque[StoredEvent] = deque(maxlen=max_events)

    # ---------------------------------------------------------
    # BaseSink
    # ---------------------------------------------------------

    def write(self, event: LogEvent):
        self._events.append(StoredEvent(event))

    # ---------------------------------------------------------
    # Collection API
    # ---------------------------------------------------------

    def __len__(self):
        return len(self._events)

    def __iter__(self) -> Iterator[StoredEvent]:
        return iter(self._events)

    def __getitem__(self, index):
        return self._events[index]

    # ---------------------------------------------------------
    # Operations
    # ---------------------------------------------------------

    def clear(self):
        self._events.clear()

    @property
    def events(self):
        return tuple(self._events)

    @property
    def selected_events(self):
        return tuple(event for event in self._events if event.selected)

    @property
    def pinned_events(self):
        return tuple(event for event in self._events if event.pinned)

    @property
    def visible_events(self):
        return tuple(event for event in self._events if event.visible)

    # ---------------------------------------------------------
    # Selection
    # ---------------------------------------------------------

    def clear_selection(self):
        for event in self._events:
            event.selected = False

    def select_all(self):
        for event in self._events:
            event.selected = True

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------

    def filter(self, predicate):
        """
        Update the visibility state of every event.

        Example:

            sink.filter(
                lambda e: e.event.severity >= Severity.WARNING
            )
        """
        for event in self._events:
            event.visible = predicate(event)
