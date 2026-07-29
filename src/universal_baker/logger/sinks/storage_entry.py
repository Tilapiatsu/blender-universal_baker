from __future__ import annotations

from dataclasses import dataclass, field
import time

from ..event import LogEvent


@dataclass(slots=True)
class StoredEvent:
    """
    Runtime representation of a LogEvent.

    A StoredEvent wraps an immutable LogEvent with mutable state that is
    useful for UI interactions (selection, filtering, pinning...).
    """

    event: LogEvent
    received_time: float = field(default_factory=time.perf_counter)
    selected: bool = False
    pinned: bool = False
    visible: bool = True
    expanded: bool = True
    user_data: dict = field(default_factory=dict)
