from __future__ import annotations

from ..logger.sinks.base import BaseSink
from .dispatcher import Dispatcher
from .event import LogEvent
from .middleware.dispatcher import MiddlewareDispatcher
from .scopes.scope_manager import ScopeManager
from .scopes.task_status import ScopeState
from .severity import Severity


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

    def scope(self, name: str, weight: float = 1.0, **metadata):
        return self.scope_manager.create_scope(
            name=name,
            weight=weight,
            **metadata,
        )

    def progress(self, value: float):
        scope = self.scope_manager.current

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
            scope_duration=scope.duration if state is ScopeState.EXIT else None,
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
