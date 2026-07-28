from .base import BaseMiddleware

from ..severity import Severity


class IgnoreDebugMiddleware(BaseMiddleware):
    def process(self, event):

        if event.severity == Severity.DEBUG:
            return None

        return event
