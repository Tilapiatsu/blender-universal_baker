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

    @classmethod
    def get_default(
        cls,
        output_path: str,
        filename_template: str = "",
        width: int = 1024,
        height: int = 1024,
        colorspace: str = "sRGB",
        export_file: bool = True,
    ):
        return cls(
            image=ImageSettings(),
            color=ColorManagementSettings(),
            path=PathSettings(
                width=width,
                height=height,
                colorspace=colorspace,
                export_file=export_file,
                output_path=output_path,
                filename_template=filename_template,
            ),
        )
