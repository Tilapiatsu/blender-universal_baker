from __future__ import annotations

from dataclasses import dataclass

import bpy


@dataclass(slots=True)
class RenderSettings:
    use_adaptive_sampling: bool = False

    adaptive_threshold: float = 0.01
    samples: int = 4096
    adaptive_min_samples: int = 0

    use_denoising: bool = False

    bake_margin: int = 16
    bake_margin_type: str = "ADJACENT_FACES"
    bake_target: str = "IMAGE_TEXTURES"

    bake_use_selected_to_active: bool = False
    bake_use_cage: bool = False
    bake_cage_object: bpy.types.object | None = None
    bake_cage_extrusion: float = 0.1
    bake_max_ray_distance: float = 0.0
