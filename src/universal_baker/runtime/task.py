from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class Task:
    """Base Task Class. This is the base class that each executor uses."""

    id: str
    uuid: str
    enabled: bool

    @property
    def output_name(self) -> str: ...


@dataclass(slots=True)
class TaskResult:
    """Every Task Return a TaskResult."""

    success: bool
    outputs: list[Path]
    warnings: list[str]
    errors: list[str]
