from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CageSettings:
    mode: str = "AUTO"
    extrusion: float = 0.1
    max_ray_distance: float = 0.0
