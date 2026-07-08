from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class BakeContext:
    """Temporary execution context.

    This object is created for the duration of a bake
    and discarded afterwards.
    """

    active_object: str | None = None
    selected_objects: list[str] = field(default_factory=list)
    temporary_images: list[Any] = field(default_factory=list)
    temporary_materials: list[Any] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)
    cancelled: bool = False
