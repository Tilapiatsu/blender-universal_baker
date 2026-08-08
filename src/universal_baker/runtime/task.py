from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .output_context import OutputContext
from ..resources.uv import UVLayout


@dataclass(slots=True, frozen=True)
class Task:
    """Base Task Class. This is the base class that each executor uses."""

    uuid: str
    enabled: bool
    output_context: OutputContext
    bake_group_uuid: str
    uv_layout: UVLayout

    @property
    def output_name(self) -> str: ...

    @property
    def absolute_filepath(self) -> Path: ...

    def __repr__(self) -> str: ...

    def notify_finished(self, time_elapsed: float) -> None: ...

    def notify_failed(self, time_elapsed: float, error: str) -> None: ...


@dataclass(slots=True)
class TaskResult:
    """Every Task Return a TaskResult."""

    success: bool
    outputs: list[Path]
    warnings: list[str]
    errors: list[str]
