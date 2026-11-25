from __future__ import annotations

import bpy

from ..severity import Severity
from ..sinks.ui.entry import EntryType, UIEntry
from ..sinks.ui.filter import UIFilter
from .icons import SEVERITY_ICONS, STATUS_ICONS


def build_ui_filter(settings) -> UIFilter:
    severities = set()

    if settings.show_debug:
        severities.add(Severity.DEBUG)

    if settings.show_info:
        severities.add(Severity.INFO)

    if settings.show_warning:
        severities.add(Severity.WARNING)

    if settings.show_error:
        severities.update((Severity.ERROR, Severity.CRITICAL))

    return UIFilter(severities=severities)


def draw_filter_controls(layout, settings):
    row = layout.row(align=True)
    row.label(text="Severity")

    row.prop(settings, "show_debug", text="Debug")
    row.prop(settings, "show_info", text="Info")
    row.prop(settings, "show_warning", text="Warning")
    row.prop(settings, "show_error", text="Error")


def _format_duration(duration: float | None) -> str:
    if duration is None:
        return ""

    if duration < 1.0:
        return f"{duration * 1000:.0f} ms"

    return f"{duration:.2f} s"


def _entry_matches_filter(entry, ui_filter: UIFilter) -> bool:
    if entry.is_scope:
        # Scope rows describe task structure and are not severity-filtered.
        return ui_filter.accepts_channel(entry.channel)

    if entry.event is None:
        return False

    return ui_filter.accepts_channel(entry.channel) and ui_filter.accepts_severity(entry.event.severity)


def _has_visible_content(entry, ui_filter: UIFilter) -> bool:
    if _entry_matches_filter(entry, ui_filter):
        return True

    return any(_has_visible_content(child, ui_filter) for child in entry.children)


def _draw_toggle(layout, entry, sink_key, action, expanded):
    if not sink_key:
        layout.label(
            text="",
            icon="TRIA_DOWN" if expanded else "TRIA_RIGHT",
        )
        return

    operator = layout.operator(
        "logger.toggle_entry",
        text="",
        icon="TRIA_DOWN" if expanded else "TRIA_RIGHT",
        emboss=False,
    )
    operator.sink_key = sink_key
    operator.entry_id = entry.id
    operator.action = action


def draw_entry(layout, entry, ui_filter, indent: int, sink_key=None):
    if not _has_visible_content(entry, ui_filter):
        return

    if entry.type is EntryType.SCOPE:
        _draw_scope(layout, entry, ui_filter, sink_key, indent)
    else:
        _draw_message(layout, entry, sink_key, indent)


def _draw_scope(layout: bpy.types.UILayout, entry: UIEntry, ui_filter: UIFilter, sink_key: str | None, indent: int):
    column = layout.column()
    row = column.row()

    if len(entry.children) > 1:
        indent = _draw_indent(
            sink_key,
            entry,
            row,
            indent,
            action="TOGGLE_EXPANDED",
        )

    else:
        indent = _draw_indent(
            None,
            None,
            row,
            indent,
            action="TOGGLE_EXPANDED",
            draw_indent=False,
        )

    row.label(
        text=entry.label,
        icon=STATUS_ICONS.get(entry.status, "DOT"),
    )

    # if entry.progress is not None:
    #     row.label(text=f"{entry.progress:.0%}")
    row = row.row()
    row.alignment = "RIGHT"

    if entry.duration is not None:
        row.label(text=_format_duration(entry.duration))

    if entry.progress is not None and entry.progress < 1.0:
        column.progress(
            factor=max(0.0, min(1.0, entry.progress)),
            type="BAR",
            text=f"{entry.progress:.0%}",
            # text="",
        )

    if entry.expanded:
        children = column.column(align=True)
        for child in entry.children:
            draw_entry(children, child, ui_filter, indent, sink_key)


def _draw_message(layout, entry, sink_key, indent: int):
    event = entry.event
    if event is None:
        return

    row = layout.row(align=True)
    indent = _draw_indent(
        sink_key=None,
        entry=None,
        layout=row,
        indent=indent,
        draw_indent=False,
    )

    if entry.has_details:
        indent = _draw_indent(sink_key, entry, row, indent, action="TOGGLE_DETAILS")

    row.label_multiline(
        text=event.message,
        icon=SEVERITY_ICONS.get(event.severity, "INFO"),
    )

    if event.category:
        row.label(text=event.category)

    if entry.details_expanded and entry.has_details:
        _draw_message_details(layout, event, indent)


def _draw_message_details(layout, event, indent: int):
    _draw_indent(
        sink_key=None,
        entry=None,
        layout=layout,
        indent=indent,
        draw_indent=False,
    )
    column = layout.column(align=True)

    if event.exception is not None:
        column.label(text=f"{type(event.exception).__name__}: {event.exception}")

    if event.traceback_text:
        column.label(text="Traceback:")
        traceback_column = column.column(align=True)

        for line in event.traceback_text.rstrip().splitlines():
            traceback_column.label(text=line)

    if event.data:
        column.separator()
        column.label(text="Additional data:")

        for key, value in event.data.items():
            value_lines = str(value).splitlines() or [""]
            column.label(text=f"{key}: {value_lines[0]}")

            for line in value_lines[1:]:
                column.label(text=f"    {line}")


def _draw_indent(
    sink_key: str | None,
    entry: UIEntry | None,
    layout: bpy.types.UILayout,
    indent: int,
    draw_indent: bool = True,
    action: str = "TOGGLE_DETAILS",
) -> int:
    for _ in range(indent):
        if not draw_indent:
            layout = layout.row()
        layout.label(text="", icon="GRIP_V")

    if draw_indent and sink_key is not None and entry is not None:
        _draw_toggle(
            layout,
            entry,
            sink_key,
            action=action,
            expanded=entry.expanded if action == "TOGGLE_EXPANDED" else entry.details_expanded,
        )
    else:
        layout.label(text="", icon="GRIP_V")

    indent += 1
    return indent


def draw_log_tree(layout, sink, ui_filter=None, sink_key=None):
    """
    Draw the complete UIEntry tree.

    Every scope has its own expanded state, including root scopes. Messages
    with exception/traceback/data have an independent details toggle.
    """

    if ui_filter is None:
        ui_filter = sink.filter

    if sink_key is None:
        sink_key = getattr(sink, "_blender_registry_key", None)

    if not sink.roots:
        layout.label(text="No log entries yet", icon="INFO")
        return

    visible_roots = [entry for entry in sink.roots if _has_visible_content(entry, ui_filter)]

    if not visible_roots:
        layout.label(text="No entries match the current filters", icon="INFO")
        return

    for entry in visible_roots:
        draw_entry(layout, entry, ui_filter, 0, sink_key)


def draw_logger_panel(layout, context, runtime):
    """
    Convenience entry point for addon panels using BlenderLoggerRuntime.
    """

    ui_sink = getattr(runtime, "ui_sink", None)
    if ui_sink is None:
        layout.label(text="No UI sink is configured", icon="INFO")
        return

    property_name = getattr(runtime, "filter_property_name", "logger_filter")
    settings = getattr(context.window_manager, property_name, None)

    if settings is not None:
        draw_filter_controls(layout, settings)
        layout.separator()
        ui_filter = build_ui_filter(settings)
    else:
        ui_filter = runtime.ui_sink.filter

    draw_log_tree(
        layout,
        runtime.ui_sink,
        ui_filter=ui_filter,
        sink_key=getattr(runtime, "ui_sink_key", None),
    )
