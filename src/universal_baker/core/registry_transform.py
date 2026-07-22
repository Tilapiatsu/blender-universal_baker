from __future__ import annotations

from typing import Callable


class TransformRegistry:
    _transforms = {}

    @classmethod
    def register(cls, name: str, callback: Callable):
        cls._transforms[name] = callback

    @classmethod
    def apply(cls, value: str, transform: str):
        callback = cls._transforms.get(transform)

        if callback is None:
            return value

        return callback(value)

    def __getitem__(self, transform: str) -> Callable:
        return self._transforms[transform]

    def exists(self, token: str) -> bool:
        return token in self._transforms

    def items(self):
        return self._transforms.items()

    def values(self):
        return self._transforms.values()

    def keys(self):
        return self._transforms.keys()


registry_transform = TransformRegistry()
