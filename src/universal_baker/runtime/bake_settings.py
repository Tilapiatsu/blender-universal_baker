from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class ImageSettings:
    width: int = 2048
    height: int = 2048
    cineon_black: int = 0
    cineon_gamma: float = 0.0
    cineon_white: int = 0
    color_depth: str = "8"
    color_management: Literal["FOLLOW_SCENE", "OVERRIDE"] = "FOLLOW_SCENE"
    color_mode: str = "RGBA"
    compression: int = 15
    exr_codec: str = "NONE"
    file_format: str = "PNG"
    has_linear_colorspace: bool = False
    jpeg2k_codec: str = "JP2"
    media_type: str = "IMAGE"
    quality: int = 90
    tiff_codec: str = "DEFLATE"
    use_cineon_log: bool = False
    use_exr_interleave: bool = False
    use_jpeg2k_cinema_48: bool = False
    use_jpeg2k_cinema_preset: bool = False
    use_jpeg2k_ycc: bool = False
    use_preview: bool = False
    views_format: str = "INDIVIDUAL"

    @property
    def float_buffer(self):
        return self.has_linear_colorspace

    @property
    def alpha(self):
        return self.color_mode == "RGBA" and self.file_format in ["PNG", "TIFF", "TARGA", "OPEN_EXR", "XDP"]


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
