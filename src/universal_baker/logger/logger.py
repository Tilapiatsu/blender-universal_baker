from .dispatcher import Dispatcher
from .event import LogEvent
from .severity import Severity
from .middleware.dispatcher import MiddlewareDispatcher


class Logger:
    def __init__(self, addon=None):
        self.addon = addon
        self.middleware = MiddlewareDispatcher()
        self.dispatcher = Dispatcher()

    def log(self, severity: Severity, message: str, **kwargs):
        event = LogEvent(severity=severity, message=message, addon=self.addon, **kwargs)

        event = self.middleware.process(event)

        if event is None:
            return

        self.dispatcher.dispatch(event)

    def debug(self, message: str, **kwargs):
        self.log(Severity.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        self.log(Severity.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        self.log(Severity.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        self.log(Severity.ERROR, message, **kwargs)
