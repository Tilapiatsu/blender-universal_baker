from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from ...event import LogEvent
from ...scopes.task_status import TaskStatus


class EntryType(Enum):
    SCOPE = auto()
    MESSAGE = auto()


@dataclass(slots=True)
class UIEntry:
    id: int
    type: EntryType
    label: str

    parent: UIEntry | None = None
    children: list[UIEntry] = field(default_factory=list)

    # Scope information
    scope_id: int | None = None
    status: TaskStatus | None = None
    progress: float | None = None
    cancellation_requested: bool = False
    duration: float | None = None

    # Message information
    event: LogEvent | None = None

    # UI presentation state. These values never affect task execution.
    expanded: bool = True
    details_expanded: bool = False
    selected: bool = False

    channel: str | None = None

    @property
    def is_scope(self) -> bool:
        return self.type is EntryType.SCOPE

    @property
    def is_message(self) -> bool:
        return self.type is EntryType.MESSAGE

    @property
    def has_details(self) -> bool:
        if self.event is None:
            return False

        return (
            self.event.exception is not None
            or self.event.traceback_text is not None
            or bool(self.event.data)
        )

    def add_child(self, child: UIEntry):
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: UIEntry):
        self.children.remove(child)
        child.parent = None

    @property
    def depth(self) -> int:
        depth = 0
        parent = self.parent

        while parent is not None:
            depth += 1
            parent = parent.parent

        return depth
