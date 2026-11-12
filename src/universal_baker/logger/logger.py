from __future__ import annotations

from contextlib import contextmanager

from .dispatcher import Dispatcher
from .event import LogEvent
from .middleware.dispatcher import MiddlewareDispatcher
from .middleware.scope_manager import ScopeManager
from .severity import Severity


class Logger:
    def __init__(self, addon=None) -> None:
        self.addon = addon
        self.middleware = MiddlewareDispatcher()
        self.dispatcher = Dispatcher()
        self.scope_manager = ScopeManager()

    def log(self, severity: Severity, message: str, **kwargs) -> None:
        event = LogEvent(
            severity=severity,
            message=message,
            addon=self.addon,
            scope=self.scope_manager.current_path,
            **kwargs,
        )

        event = self.middleware.process(event)

        if event is None:
            return

        self.dispatcher.dispatch(event)

    @contextmanager
    def scope(self, name: str | None, **metadata):
        if name is not None:
            with self.scope_manager.scope(name, **metadata):
                yield
        else:
            yield

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
