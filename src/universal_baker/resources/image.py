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
    _width: int = 2048
    _height: int = 2048

    filepath: Path = field(default_factory=Path)
    name: str = ""

    generated_type: str = "BLANK"

    tiles: bool = False

    object_name: str = ""
    map_name: str = ""

    channels: int = 4
    colorspace: str = "sRGB"
    is_data: bool = False

    image_format_settings: ImageSettings | None = None

    created: bool = False
    loaded: bool = False
    saved: bool = False
    dirty: bool = False
    temporary: bool = False
    packed: bool = False
    is_copy: bool = False

    @classmethod
    def create(
        cls,
        width: int,
        height: int,
        name: str,
        filepath: Path,
        colorspace: str,
        alpha: bool = False,
        float_buffer: bool = False,
        tiles: bool = False,
    ) -> ImageResource:
        image = bpy.data.new(
            name,
            width,
            height,
            alpha,
            float_buffer,
            stereo3d=False,
            is_data=True if colorspace == "Non-Color" else False,
            tiles=tiles,
        )
        return cls(
            image=image,
            _width=width,
            _height=height,
            name=name,
            filepath=filepath,
            channels=4 if alpha else 3,
            tiles=tiles,
        )

    @property
    def width(self) -> int:
        if self.image is None:
            return self._width
        return self.image.size[0]

    @width.setter
    def width(self, value) -> None:
        self._width = value

    @property
    def height(self) -> int:
        if self.image is None:
            return self._height
        return self.image.size[1]

    @height.setter
    def height(self, value) -> None:
        self._height = value

    @property
    def exists(self) -> bool:
        return self.image is not None

    @property
    def filename(self) -> str:
        return self.filepath.name

    @property
    def directory(self) -> Path | None:
        if self.filepath is None:
            return None
        return self.filepath.parent

    def scale(self, width: int, height: int) -> None:
        if self.image is None:
            return
        self.image.scale(width, height)

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

    def reset(self):
        self.filepath = Path("")
        self.image = None
        self.created = False
        self.created = False
        self.loaded = False
        self.saved = False
        self.dirty = False
        self.temporary = False
        self.packed = False
        self.is_copy = False

    def init_from_image(self) -> None:
        if self.image is None:
            return

        self._width = self.image.size[0]
        self._height = self.image.size[1]
        self.name = self.image.name
        self.filepath = self.image.filepath_raw
        self.tiles = self.image.tiles

    def __repr__(self) -> str:
        result = ""
        result += f"{self.name} : {self.filepath}\nwidth = {self.width}\nheight = {self.height}"
        return result
