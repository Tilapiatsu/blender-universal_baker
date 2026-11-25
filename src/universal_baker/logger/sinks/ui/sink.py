from __future__ import annotations

from collections.abc import Iterator
from itertools import count

from ...event import LogEvent
from ...scopes.task_status import ScopeState
from ...severity import Severity
from ..base import BaseSink
from .entry import EntryType, UIEntry
from .filter import UIFilter


class UISink(BaseSink):
    def __init__(
        self,
        level: Severity = Severity.INFO,
        channels: set[str] | None = None,
        severities: set[Severity] | None = None,
    ):
        super().__init__(level)

        self.filter = UIFilter(
            channels=channels,
            level=level,
            severities=severities,
        )

        self._roots: list[UIEntry] = []
        self._scope_entries: dict[int, UIEntry] = {}
        self._entries_by_id: dict[int, UIEntry] = {}
        self._ids = count(1)
        self._listeners = []

    # ---------------------------------------------------------
    # Public access
    # ---------------------------------------------------------

    @property
    def roots(self) -> tuple[UIEntry, ...]:
        return tuple(self._roots)

    @property
    def scope_entries(self) -> dict[int, UIEntry]:
        return dict(self._scope_entries)

    def iter_entries(self) -> Iterator[UIEntry]:
        """Iterate recursively through the complete entry tree."""

        def walk(entries):
            for entry in entries:
                yield entry
                yield from walk(entry.children)

        return walk(self._roots)

    def clear(self):
        self._roots.clear()
        self._scope_entries.clear()
        self._entries_by_id.clear()
        self._notify_changed()

    # ---------------------------------------------------------
    # Event acceptance and receiving
    # ---------------------------------------------------------

    def accepts(self, event: LogEvent) -> bool:
        # Filtering is deliberately presentation-only. Do not discard events
        # based on severity or channel when they enter the sink.
        return event.display_in_ui

    def write(self, event: LogEvent):
        if event.scope_state is not None:
            self._write_scope_event(event)
        else:
            self._write_message_event(event)

        self._notify_changed()

    # ---------------------------------------------------------
    # Scope events
    # ---------------------------------------------------------

    def _write_scope_event(self, event: LogEvent):
        scope_id = event.scope_id

        if scope_id is None:
            return

        entry = self._scope_entries.get(scope_id)

        if event.scope_state in (ScopeState.CREATE, ScopeState.ENTER):
            if entry is None:
                entry = self._create_scope_entry(event)

        elif entry is None:
            # An UPDATE/EXIT without a corresponding CREATE is ignored.
            return

        entry.label = event.message
        entry.status = event.task_status
        entry.progress = event.progress
        entry.cancellation_requested = event.cancellation_requested

        if event.scope_duration is not None:
            entry.duration = event.scope_duration

        # Metadata can be updated during the lifetime of a scope.
        if event.ui_channel is not None:
            entry.channel = event.ui_channel
        elif event.scope_metadata.get("ui_channel") is not None:
            entry.channel = event.scope_metadata["ui_channel"]

    def _create_scope_entry(self, event: LogEvent) -> UIEntry:
        entry_id = next(self._ids)

        entry = UIEntry(
            id=entry_id,
            type=EntryType.SCOPE,
            label=event.message,
            scope_id=event.scope_id,
            status=event.task_status,
            progress=event.progress,
            cancellation_requested=event.cancellation_requested,
            duration=event.scope_duration,
            channel=event.ui_channel or event.scope_metadata.get("ui_channel"),
        )

        self._scope_entries[event.scope_id] = entry
        self._entries_by_id[entry_id] = entry

        parent = self._scope_entries.get(event.parent_scope_id)

        if parent is not None:
            parent.add_child(entry)
        else:
            self._roots.append(entry)

        return entry

    # ---------------------------------------------------------
    # Log messages
    # ---------------------------------------------------------

    def _write_message_event(self, event: LogEvent):
        entry_id = next(self._ids)

        entry = UIEntry(
            id=entry_id,
            type=EntryType.MESSAGE,
            label=event.message,
            event=event,
            channel=event.ui_channel,
        )

        self._entries_by_id[entry_id] = entry

        parent = self._scope_entries.get(event.scope_id)

        if parent is not None:
            parent.add_child(entry)
        else:
            self._roots.append(entry)

    # ---------------------------------------------------------
    # Runtime filtering
    # ---------------------------------------------------------

    def set_filter(self, ui_filter: UIFilter):
        self.filter = ui_filter
        self._notify_changed()

    def is_visible(self, entry: UIEntry) -> bool:
        if entry.is_scope:
            return self.filter.accepts_channel(entry.channel)

        if entry.event is None:
            return False

        return (
            self.filter.accepts_channel(entry.channel)
            and self.filter.accepts_severity(entry.event.severity)
        )

    # ---------------------------------------------------------
    # Entry interaction
    # ---------------------------------------------------------

    def get_entry(self, entry_id: int) -> UIEntry | None:
        return self._entries_by_id.get(entry_id)

    def toggle_entry(self, entry_id: int) -> bool:
        entry = self.get_entry(entry_id)

        if entry is None or not entry.is_scope:
            return False

        entry.expanded = not entry.expanded
        self._notify_changed()
        return True

    def toggle_details(self, entry_id: int) -> bool:
        entry = self.get_entry(entry_id)

        if entry is None or not entry.is_message or not entry.has_details:
            return False

        entry.details_expanded = not entry.details_expanded
        self._notify_changed()
        return True

    # ---------------------------------------------------------
    # Listeners
    # ---------------------------------------------------------

    def add_listener(self, callback):
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback):
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify_changed(self):
        for callback in tuple(self._listeners):
            callback()
