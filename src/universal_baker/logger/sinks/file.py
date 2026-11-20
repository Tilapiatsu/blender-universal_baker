from __future__ import annotations

import os
import re
import tempfile
import traceback
from datetime import datetime
from pathlib import Path

from ..event import LogEvent
from ..severity import Severity
from .base import BaseSink


class FileSink(BaseSink):
    DEFAULT_MAX_BYTES = 5 * 512 * 512

    def __init__(
        self,
        directory: str | Path | None = None,
        filename: str = "addon.log",
        level: Severity = Severity.INFO,
        max_files: int = 10,
        max_bytes: int | None = DEFAULT_MAX_BYTES,
        flush: bool = True,
    ):
        super().__init__(level)

        if max_files < 1:
            raise ValueError("max_files must be at least 1")

        if max_bytes is not None and max_bytes < 1:
            raise ValueError("max_bytes must be positive or None")

        self.directory = Path(directory) if directory is not None else Path(tempfile.gettempdir()) / "blender_addons"

        self.filename = filename
        self.max_files = max_files
        self.max_bytes = max_bytes
        self.flush = flush

        self.path = self.directory / filename

        self._file = None
        self._current_size = 0

        self.directory.mkdir(parents=True, exist_ok=True)

        # Remove archives outside the configured retention limit.
        self._prune_archives()

        self._open()

    # ---------------------------------------------------------
    # File management
    # ---------------------------------------------------------

    def _open(self):
        self._file = self.path.open("ab")
        self._current_size = self.path.stat().st_size

    def _close_file(self):
        if self._file is None:
            return

        self._file.flush()
        self._file.close()
        self._file = None

    def close(self):
        self._close_file()

    def flush_file(self):
        if self._file is not None:
            self._file.flush()

    def _archive_path(self, index: int) -> Path:
        return self.path.with_name(f"{self.path.stem}_{index:02d}{self.path.suffix}")

    def _prune_archives(self):
        """Remove archives whose index exceeds the retention limit."""

        pattern = re.compile(
            rf"^{re.escape(self.path.stem)}_(\d+)"
            rf"{re.escape(self.path.suffix)}$"
        )

        for candidate in self.directory.iterdir():
            match = pattern.match(candidate.name)

            if not match:
                continue

            index = int(match.group(1))

            if index >= self.max_files:
                candidate.unlink()

    def _rotate(self):
        self._close_file()
        self._prune_archives()

        if self.max_files == 1:
            self.path.unlink(missing_ok=True)

        else:
            # Shift existing archives, starting with the oldest.
            for index in range(self.max_files - 1, 1, -1):
                source = self._archive_path(index - 1)
                destination = self._archive_path(index)

                if source.exists():
                    os.replace(source, destination)

            # Move the current log to archive 01.
            if self.path.exists():
                os.replace(
                    self.path,
                    self._archive_path(1),
                )

        self._open()

    # ---------------------------------------------------------
    # Event formatting
    # ---------------------------------------------------------

    def format_event(self, event: LogEvent) -> str:
        timestamp = datetime.fromtimestamp(event.timestamp).astimezone().strftime("%Y-%m-%d %H:%M:%S")

        parts = [
            timestamp,
            f"[{event.severity.name}]",
        ]

        if event.addon:
            parts.append(f"[{event.addon}]")

        if event.category:
            parts.append(f"[{event.category}]")

        scope = getattr(event, "scope", None)

        if scope:
            if isinstance(scope, (tuple, list)):
                scope_name = " > ".join(map(str, scope))
            else:
                scope_name = str(scope)

            parts.append(f"[{scope_name}]")

        line = " ".join(parts) + f" {event.message}"

        exception = event.exception

        if exception is not None:
            line += "\n" + "".join(
                traceback.format_exception(
                    type(exception),
                    exception,
                    exception.__traceback__,
                )
            )

        return line

    # ---------------------------------------------------------
    # Writing
    # ---------------------------------------------------------

    def write(self, event: LogEvent):
        if self._file is None:
            self._open()

        assert self._file is not None

        content = self.format_event(event)
        payload = (content + "\n").encode("utf-8")

        # Rotate before writing the event.
        # Keep a single oversized event in an otherwise empty file.
        if self.max_bytes is not None and self._current_size > 0 and self._current_size + len(payload) > self.max_bytes:
            self._rotate()

        self._file.write(payload)
        self._current_size += len(payload)

        if self.flush:
            self._file.flush()
