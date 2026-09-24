from __future__ import annotations

from dataclasses import dataclass

from .settings_image import ColorManagementSettings, ImageSettings


@dataclass(slots=True)
class PathSettings:
    width: int
    height: int
    colorspace: str
    export_file: bool
    output_path: str
    filename_template: str


@dataclass(slots=True)
class OutputSettings:
    image: ImageSettings
    color: ColorManagementSettings
    path: PathSettings
