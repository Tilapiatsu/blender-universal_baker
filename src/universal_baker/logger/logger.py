from __future__ import annotations

import traceback

from .dispatcher import Dispatcher
from .event import LogEvent
from .middleware.dispatcher import MiddlewareDispatcher
from .scopes.scope_manager import ScopeManager
from .scopes.task_status import ScopeState
from .severity import Severity
from .sinks.base import BaseSink
from .sinks.ui.sink import UISink


class Logger:
    def __init__(self, addon=None) -> None:
        self.addon = addon
        self.middleware = MiddlewareDispatcher()
        self.dispatcher = Dispatcher()
        self.scope_manager = ScopeManager(emit_callback=self._emit_scope_event)

    def log(self, severity, message, **kwargs):
        scope = self.scope_manager.current

        kwargs.setdefault("display_in_ui", False)

        if scope is not None:
            kwargs.setdefault("scope", scope.path)
            kwargs.setdefault("scope_id", scope.id)
            kwargs.setdefault("ui_channel", scope.metadata.get("ui_channel"))

        exception = kwargs.get("exception")
        if exception is not None and kwargs.get("traceback_text") is None:
            kwargs["traceback_text"] = "".join(
                traceback.format_exception(
                    type(exception),
                    exception,
                    exception.__traceback__,
                )
            )

        event = LogEvent(
            severity=severity,
            message=message,
            addon=self.addon,
            **kwargs,
        )
        event = self.middleware.process(event)

        if event is not None:
            self.dispatcher.dispatch(event)

    def get_sink(self, name: str) -> BaseSink | None:
        return self.dispatcher.get(name)

    @property
    def ui_sinks(self) -> list[UISink]:
        return self.dispatcher.get_by_type(UISink.__name__)

    def scope(self, name: str, weight: float = 1.0, *, detached: bool = False, parent=None, **metadata):
        return self.scope_manager.create_scope(
            name=name,
            weight=weight,
            detached=detached,
            parent=parent,
            **metadata,
        )

    def detached_scope(self, name: str, weight: float = 1.0, *, parent=None, **metadata):
        """Create a scope without implicitly attaching it to the active stack."""
        clear_ui_logs = metadata.get("clear_ui_logs", None)
        if clear_ui_logs:
            ui_sinks = self.ui_sinks
            for s in ui_sinks:
                s.clear()

        return self.scope(name, weight, detached=True, parent=parent, **metadata)

    def bind_scope(self, scope):
        """Temporarily bind a running detached scope for log attribution."""
        return self.scope_manager.bind(scope)

    def progress(self, value: float, scope=None):
        scope = scope or self.scope_manager.current

        if scope is None:
            raise RuntimeError("No active scope")

        scope.set_progress(value)

    def _emit_scope_event(self, scope, state: ScopeState):
        event = LogEvent(
            severity=Severity.INFO,
            message=scope.name,
            addon=self.addon,
            scope_id=scope.id,
            parent_scope_id=scope.parent.id if scope.parent else None,
            scope=scope.path,
            scope_state=state,
            task_status=scope.status,
            progress=scope.progress,
            cancellation_requested=scope.cancellation_requested,
            scope_duration=scope.duration,
            scope_metadata=dict(scope.metadata),
            display_in_ui=scope.metadata.get("display_in_ui", True),
            ui_channel=scope.metadata.get("ui_channel"),
        )

        self.dispatcher.dispatch(event)

    def debug(self, message: str, **kwargs) -> None:
        self.log(Severity.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        self.log(Severity.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        self.log(Severity.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        self.log(Severity.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        self.log(Severity.CRITICAL, message, **kwargs)

    def separator(self, severity: Severity, **kwargs) -> None:
        self.log(severity, "=" * 100, **kwargs)

    def close(self):
        self.dispatcher.close()
