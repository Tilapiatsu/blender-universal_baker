from __future__ import annotations
from dataclasses import dataclass

from .settings_image import ImageSettings


@dataclass(slots=True)
class PackSettings:
    image: ImageSettings
