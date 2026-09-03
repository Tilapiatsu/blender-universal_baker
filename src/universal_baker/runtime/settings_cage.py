from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CageSettings:
    mode: str = "NONE"
    cage_extrusion: float = 0.1
    max_ray_distance: float = 0.0
    extrusion_group: str = "UBK_EXTRUSION_GROUP"
    skew_map: str = "UBK_SKEW_MAP"
