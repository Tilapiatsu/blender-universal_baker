from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4
from pathlib import Path


@dataclass(slots=True, frozen=True)
class Task:
    """Base Task Class. This is the base class that each executor uses."""

    id: str
    enabled: bool

    @classmethod
    def create(cls):
        return cls(
            id=str(uuid4()),
            enabled=True,
        )


@dataclass(slots=True)
class TaskResult:
    """Every Task Return a TaskResult."""

    success: bool
    outputs: list[Path]
    warnings: list[str]
    errors: list[str]
