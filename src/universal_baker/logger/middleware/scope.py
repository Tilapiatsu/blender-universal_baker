from __future__ import annotations

from contextlib import contextmanager
from typing import Generator


class ScopeManager:
    def __init__(self) -> None:
        self._stack = []

    @property
    def current(self) -> tuple:
        return tuple(self._stack)

    def push(self, name: str) -> None:
        self._stack.append(name)

    def pop(self) -> None:
        if self._stack:
            self._stack.pop()

    @contextmanager
    def scope(self, name: str) -> Generator:
        self.push(name)

        try:
            yield

        finally:
            self.pop()
