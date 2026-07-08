from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any


class BakeTaskStatus(Enum):
    """Execution state of a bake task."""

    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass(slots=True)
class BakeTaskState:
    status: BakeTaskStatus = BakeTaskStatus.PENDING
    progress: float = 0.0
    image: Any | None = None
    error: str = ""


@dataclass(slots=True)
class BakeTask:
    """A single bake operation.

    Example:

        Cube
            └── Diffuse

    becomes one BakeTask.
    """

    object_name: str
    baker_id: str
    image_name: str
    enabled: bool = True
    output_path: Path | None = None
    state: BakeTaskState = BakeTaskState()
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def finished(self) -> bool:
        return self.state.status in {
            BakeTaskStatus.COMPLETED,
            BakeTaskStatus.FAILED,
            BakeTaskStatus.CANCELLED,
        }
