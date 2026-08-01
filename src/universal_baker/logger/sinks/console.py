from datetime import datetime

from .base import BaseSink
from ..event import LogEvent, ScopeState


class ConsoleSink(BaseSink):
    def write(self, event: LogEvent) -> None:
        timestamp = datetime.fromtimestamp(event.timestamp).strftime("%H:%M:%S")

        scope = ""
        if event.scope:
            scope = "[" + " > ".join(event.scope) + "] "

        severity = event.severity.name
        if len(severity) == 4:
            severity = f" {severity}  "
        elif len(severity) == 5:
            severity = f" {severity} "

        message = f"[{timestamp}] [{severity}] {scope}{event.message}"
        match event.scope_state:
            case ScopeState.ENTER:
                pass
            case ScopeState.UPDATE:
                message += f" {event.progress:.0%}"
            case ScopeState.EXIT:
                message += f" ({event.scope_duration:.2f}s)"
            case _:
                pass

        print(message)
