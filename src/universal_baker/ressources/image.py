from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import bpy
from ..runtime.settings_image import ImageSettings


@dataclass(slots=True)
class ImageResource:
    """
    Runtime wrapper around a Blender image datablock.

    This object stores both the Blender Image and all metadata
    required by the baking pipeline.
    """

    image: bpy.types.Image | None = None

    name: str = ""
    filepath: Path | None = None

    width: int = 2048
    height: int = 2048
    generated_type: str = "BLANK"

    object_name: str = ""
    map_name: str = ""

    colorspace: str = "sRGB"
    is_data: bool = False

    image_format_settings: ImageSettings | None = None

    created: bool = False
    loaded: bool = False
    saved: bool = False
    dirty: bool = False
    temporary: bool = False
    packed: bool = False

    @property
    def exists(self) -> bool:
        return self.image is not None

    @property
    def filename(self) -> str:
        if self.filepath is None:
            return ""
        return self.filepath.name

    @property
    def directory(self) -> Path | None:
        if self.filepath is None:
            return None
        return self.filepath.parent

    def mark_dirty(self) -> None:
        self.dirty = True

    def mark_saved(self) -> None:
        self.saved = True
        self.dirty = False

    def mark_temporary(self) -> None:
        self.temporary = True

    def validate(self) -> None:
        if self.width <= 0:
            raise ValueError("Image width must be greater than zero.")

        if self.height <= 0:
            raise ValueError("Image height must be greater than zero.")
