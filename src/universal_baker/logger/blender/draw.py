from __future__ import annotations

import traceback

from ..severity import Severity
from ..sinks.ui.entry import EntryType
from .icons import SEVERITY_ICONS, STATUS_ICONS


def _format_duration(duration: float | None) -> str:
    if duration is None:
        return ""

    if duration < 1.0:
        return f"{duration * 1000:.0f} ms"

    return f"{duration:.2f} s"


def _entry_matches_filter(entry, ui_filter) -> bool:
    if entry.is_scope:
        return ui_filter.accepts_channel(entry.channel)

    if entry.event is None:
        return False

    return ui_filter.accepts_channel(entry.channel) and ui_filter.accepts_severity(entry.event.severity)


def _has_visible_content(entry, ui_filter) -> bool:
    if _entry_matches_filter(entry, ui_filter):
        return True

    return any(_has_visible_content(child, ui_filter) for child in entry.children)


def draw_entry(layout, entry, ui_filter, depth=0):
    """
    Draw an entry and its visible descendants.

    Scope entries are drawn as boxes.
    Message entries are drawn as diagnostic rows.
    """

    if not _has_visible_content(entry, ui_filter):
        return

    if entry.type is EntryType.SCOPE:
        _draw_scope(layout, entry, ui_filter, depth)
    else:
        _draw_message(layout, entry)


def _draw_scope(layout, entry, ui_filter, depth):
    box = layout.box()
    column = box.column(align=True)

    row = column.row(align=True)

    icon = STATUS_ICONS.get(entry.status, "DOT")

    row.label(
        text=entry.label,
        icon=icon,
    )

    if entry.progress is not None:
        row.label(text=f"{entry.progress:.0%}")

    if entry.duration is not None:
        row.label(text=_format_duration(entry.duration))

    # Progress bar for active or completed scopes.
    if entry.progress is not None:
        progress = max(0.0, min(1.0, entry.progress))

        column.progress(
            factor=progress,
            type="BAR",
            text="",
        )

    for child in entry.children:
        draw_entry(
            column,
            child,
            ui_filter,
            depth + 1,
        )


def _draw_message(layout, entry):
    event = entry.event

    if event is None:
        return

    severity = event.severity
    icon = SEVERITY_ICONS.get(severity, "INFO")

    row = layout.row(align=True)

    row.label(
        text=event.message,
        icon=icon,
    )

    if event.category:
        row.label(text=event.category)

    # Display additional information for warnings/errors.
    if severity >= Severity.WARNING:
        _draw_message_details(layout, event)


def _draw_message_details(layout, event):
    has_details = event.exception is not None or bool(event.data)

    if not has_details:
        return

    box = layout.box()
    column = box.column(align=True)

    if event.exception is not None:
        exception_text = "".join(
            traceback.format_exception(
                type(event.exception),
                event.exception,
                event.exception.__traceback__,
            )
        )

        column.label(text=str(event.exception))
        column.label(text=exception_text[:1000])

    for key, value in event.data.items():
        column.label(
            text=f"{key}: {value}",
        )


def draw_log_tree(layout, sink):
    """
    Entry point for addon panels.
    """

    if not sink.roots:
        layout.label(
            text="No log entries yet",
            icon="INFO",
        )
        return

    ui_filter = sink.filter

    for entry in sink.roots:
        if not _has_visible_content(entry, ui_filter):
            continue

        if entry.type is EntryType.SCOPE:
            header, body = layout.panel(
                f"logger_scope_{entry.id}",
                default_closed=False,
            )

            if header is None:
                continue

            header_row = header.row(align=True)

            header_row.label(
                text=entry.label,
                icon=STATUS_ICONS.get(entry.status, "DOT"),
            )

            if entry.progress is not None:
                header_row.label(
                    text=f"{entry.progress:.0%}",
                )

            if entry.duration is not None:
                header_row.label(
                    text=_format_duration(entry.duration),
                )

            if body is not None:
                if entry.progress is not None:
                    body.progress(
                        factor=max(
                            0.0,
                            min(1.0, entry.progress),
                        ),
                        type="BAR",
                        text="",
                    )

                for child in entry.children:
                    draw_entry(
                        body,
                        child,
                        ui_filter,
                    )

        else:
            draw_entry(
                layout,
                entry,
                ui_filter,
            )
