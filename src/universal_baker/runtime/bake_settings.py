from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ImageSettings:
    width: int = 2048
    height: int = 2048
    file_format: str = "PNG"
    color_depth: str = "8"
    alpha: bool = False
    float_buffer: bool = False


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
class ColorManagementSettings:
    colorspace: str = "sRGB"


@dataclass(slots=True)
class BakeSettings:
    image: ImageSettings
    bake: BakeRenderSettings
    sampling: SamplingSettings
    color: ColorManagementSettings
