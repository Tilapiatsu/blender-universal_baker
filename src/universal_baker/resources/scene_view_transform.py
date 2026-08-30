from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class SceneViewTransform:
    view_transform: str = "Raw"
    exposure: float = 0.0
    gamma: float = 1.0
