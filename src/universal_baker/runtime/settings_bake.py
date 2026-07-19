from __future__ import annotations

from dataclasses import dataclass

from .settings_output import OutputSettings


@dataclass(slots=True)
class BakeRenderSettings:
    margin: int = 16
    margin_type: str = "ADJACENT_FACES"
    # supersampling: str = "1"
    # upsampling: str = "1"
    target: str = "IMAGE_TEXTURES"
    use_clear: bool = True
    use_multires: bool = False


@dataclass(slots=True)
class SamplingSettings:
    adaptive_sampling: bool = False
    samples: int = 64
    noise_threshold: float = 0.01
    min_samples: int = 0
    max_samples: int = 512
    denoise: bool = False


@dataclass(slots=True)
class BakeSettings(OutputSettings):
    bake: BakeRenderSettings
    sampling: SamplingSettings
