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

        self._roots = []
        self._scope_entries = {}
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
        self._notify_changed()

    # ---------------------------------------------------------
    # Filtering
    # ---------------------------------------------------------
    def accepts(self, event: LogEvent) -> bool:
        if event.scope_state is not None:
            return event.display_in_ui

        return event.display_in_ui

    # def accepts(self, event: LogEvent) -> bool:
    #     # Scope lifecycle events are not filtered by severity.
    #     if event.scope_state is not None:
    #         if not getattr(event, "display_in_ui", True):
    #             return False
    #
    #         channel = getattr(event, "ui_channel", None)
    #
    #         if channel is None:
    #             channel = event.scope_metadata.get("ui_channel")
    #
    #         return self.filter.accepts_channel(channel)
    #
    #     # Ordinary log messages must explicitly opt into UI display.
    #     if not getattr(event, "display_in_ui", False):
    #         return False
    #
    #     if not self.filter.accepts_severity(event.severity):
    #         return False
    #
    #     return self.filter.accepts_channel(getattr(event, "ui_channel", None))

    # ---------------------------------------------------------
    # Receiving events
    # ---------------------------------------------------------

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
            return

        # Update the existing entry.
        entry.label = event.message
        entry.status = event.task_status
        entry.progress = event.progress
        entry.duration = event.scope_duration

    def _create_scope_entry(self, event: LogEvent) -> UIEntry:
        entry = UIEntry(
            id=next(self._ids),
            type=EntryType.SCOPE,
            label=event.message,
            scope_id=event.scope_id,
            status=event.task_status,
            progress=event.progress,
            duration=event.scope_duration,
            channel=event.ui_channel or event.scope_metadata.get("ui_channel"),
        )

        self._scope_entries[event.scope_id] = entry

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
        entry = UIEntry(
            id=next(self._ids),
            type=EntryType.MESSAGE,
            label=event.message,
            event=event,
            channel=event.ui_channel,
        )

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

    def is_visible(self, entry: UIEntry) -> bool:
        if entry.is_scope:
            return self.filter.accepts_channel(entry.channel)

        if entry.event is None:
            return False

        return self.filter.accepts_channel(entry.channel) and self.filter.accepts_severity(entry.event.severity)

    # ---------------------------------------------------------
    # Listeners
    # ---------------------------------------------------------

    def add_listener(self, callback):
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback):
        if callback in self._listeners:
            self._listeners.remove(callback)

    # TODO: Need to run self._notify_changed() after changing filters if the filter is part of the sink's presentation state.
    def _notify_changed(self):
        for callback in tuple(self._listeners):
            callback()
