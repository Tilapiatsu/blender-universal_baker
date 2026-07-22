from __future__ import annotations

from typing import Callable


class TokenRegistry:
    _tokens: dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str, callback: Callable):
        cls._tokens[name] = callback

    @classmethod
    def unregister(cls, name: str):
        cls._tokens.pop(name, None)

    @classmethod
    def resolve(cls, token: str, context):
        callback = cls._tokens.get(token)

        if callback is None:
            return ""

        return str(callback(context))

    def __getitem__(self, baker_id: str) -> Callable:
        return self._tokens[baker_id]

    def exists(self, token: str) -> bool:
        return token in self._tokens

    def items(self):
        return self._tokens.items()

    def values(self):
        return self._tokens.values()

    def keys(self):
        return self._tokens.keys()


registry_token = TokenRegistry()
