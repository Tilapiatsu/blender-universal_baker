from __future__ import annotations

from dataclasses import dataclass, field

from ...severity import Severity


@dataclass(slots=True)
class UIFilter:
    # None means all channels.
    channels: set[str] | None = None

    # Minimum severity for ordinary log messages.
    level: Severity = Severity.INFO

    # Optional exact severity selection.
    severities: set[Severity] | None = None

    def accepts_channel(self, channel: str | None) -> bool:
        if self.channels is None:
            return True

        return channel in self.channels

    def accepts_severity(self, severity: Severity) -> bool:
        if self.severities is not None:
            return severity in self.severities

        return severity >= self.level
