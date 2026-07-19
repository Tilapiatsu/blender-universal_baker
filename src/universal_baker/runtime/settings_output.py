from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .settings_image import ImageSettings, ColorManagementSettings


@dataclass(slots=True)
class OutputSettings:
    image: ImageSettings
    color: ColorManagementSettings
