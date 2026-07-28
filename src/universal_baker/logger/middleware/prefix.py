from dataclasses import replace

from .base import BaseMiddleware


class PrefixMiddleware(BaseMiddleware):
    def __init__(self, prefix):
        self.prefix = prefix

    def process(self, event):

        return replace(event, message=f"{self.prefix} {event.message}")
