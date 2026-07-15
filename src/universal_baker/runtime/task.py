from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4


@dataclass(slots=True, frozen=True)
class Task:
    id: str
    enabled: bool

    @classmethod
    def create(cls):
        return cls(
            id=str(uuid4()),
            enabled=True,
        )
