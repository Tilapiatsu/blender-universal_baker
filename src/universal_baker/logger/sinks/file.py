from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path

from ..event import LogEvent
from ..severity import Severity
from .base import BaseSink


class FileSink(BaseSink):
    def __init__(
        self,
        path: str | Path | None = None,
        level: Severity = Severity.INFO,
        filename: str = "addon.log",
        flush: bool = True,
    ):
        super().__init__(level)

        self.filename = filename
        self.flush = flush

        self._file = None

        self.path = self._resolve_path(path)

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._open()

    # ---------------------------------------------------------
    # Path
    # ---------------------------------------------------------

    def _resolve_path(self, path: str | Path | None) -> Path:
        if path is None:
            return Path(tempfile.gettempdir()) / "blender_addons" / self.filename

        path = Path(path)

        # If the user provides a directory,
        # put the default filename inside it.
        if path.suffix == "":
            return path / self.filename

        return path

    # ---------------------------------------------------------
    # File handling
    # ---------------------------------------------------------

    def _open(self):
        self._file = self.path.open(
            mode="a",
            encoding="utf-8",
        )

    def close(self):
        if self._file is None:
            return

        try:
            self._file.flush()
            self._file.close()

        finally:
            self._file = None

    def flush_file(self):
        if self._file is not None:
            self._file.flush()

    # ---------------------------------------------------------
    # Formatting
    # ---------------------------------------------------------

    def format_event(self, event: LogEvent) -> str:
        timestamp = datetime.fromtimestamp(event.timestamp).strftime("%Y-%m-%d %H:%M:%S")

        scope = ""

        if event.scope:
            scope = " [" + " > ".join(event.scope) + "]"

        category = ""

        if event.category:
            category = f" [{event.category}]"

        severity = event.severity.name
        if len(severity) == 4:
            severity = f" {severity}  "
        elif len(severity) == 5:
            severity = f" {severity} "

        return f"{timestamp} [{severity}]{category}{scope} {event.message}"

    # ---------------------------------------------------------
    # Sink
    # ---------------------------------------------------------

    def write(self, event: LogEvent):
        if self._file is None:
            self._open()

        assert self._file is not None

        line = self.format_event(event)

        self._file.write(line + "\n")

        if self.flush:
            self._file.flush()
