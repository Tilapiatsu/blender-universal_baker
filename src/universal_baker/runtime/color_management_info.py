from __future__ import annotations

from dataclasses import dataclass

from ..enum.view_transform import DisplayDevice, ViewTransform


@dataclass
class ColorManagementInfo:
    apply_view_transform: bool = False

    display_device: DisplayDevice = DisplayDevice.SRGB
    view_transform: ViewTransform = ViewTransform.STANDARD
    look: str = "None"

    exposure: float = 0.0
    gamma: float = 1.0
