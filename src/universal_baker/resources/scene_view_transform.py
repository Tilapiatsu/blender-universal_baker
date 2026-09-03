from __future__ import annotations

from dataclasses import dataclass

from ..enum.view_transform import ViewTransform


@dataclass(slots=True, frozen=True)
class SceneViewTransform:
    view_transform: ViewTransform = ViewTransform.RAW
    exposure: float = 0.0
    gamma: float = 1.0
