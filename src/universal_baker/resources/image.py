from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import bpy
from ..constant import LOG
from ..runtime.settings_image import ImageSettings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..runtime.output_artifact import OutputArtifact

LOG_SCOPE = "Image Resource"


@dataclass(slots=True)
class ImageResource:
    """
    Runtime wrapper around a Blender image datablock.

    This object stores both the Blender Image and all metadata
    required by the baking pipeline.

    Answers how to interact with Blender (bpy.types.Image), but only when baking or previewing.
    """

    image: bpy.types.Image | None = None
    _width: int = 2048
    _height: int = 2048

    _filepath: Path = field(default_factory=Path)
    name: str = ""

    generated_type: str = "BLANK"

    is_udim: bool = False

    object_name: str = ""
    map_name: str = ""

    channels: int = 4
    colorspace: str = "sRGB"
    is_data: bool = False
    float_buffer: bool = False

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
        image_format_settings: ImageSettings,
        alpha: bool = False,
        float_buffer: bool = False,
        is_udim: bool = False,
    ) -> ImageResource:
        image = bpy.data.new(
            name,
            width,
            height,
            alpha,
            float_buffer,
            stereo3d=False,
            is_data=True if colorspace == "Non-Color" else False,
            tiles=is_udim,
        )
        return cls(
            image=image,
            _width=width,
            _height=height,
            name=name,
            _filepath=filepath,
            float_buffer=float_buffer,
            channels=4 if alpha else 3,
            is_udim=is_udim,
            created=True,
            image_format_settings=image_format_settings,
        )

    @property
    def filepath(self) -> Path:
        return self._filepath

    @filepath.setter
    def filepath(self, value: Path) -> None:
        self._filepath = value

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

    @property
    def tiles(self) -> list[bpy.types.UDIMTile]:
        if self.image is None:
            return []

        if self.image.tiles is None:
            return []

        return self.image.tiles.values()

    @property
    def tile_numbers(self) -> set[int]:
        tile_number = set([t.number for t in self.tiles])
        return tile_number

    def reload(self) -> None:
        if self.image is None:
            with LOG.scope(LOG_SCOPE):
                LOG.warning("Image is None : Can't reload")
            return
        self.image.reload()

    def tiles_has_changed(self, tile_numbers: set[int]) -> bool:
        if self.image is None:
            return True

        return len(tile_numbers.difference(self.tile_numbers)) > 0

    def remove_image(self) -> None:
        if self.image is None:
            return

        bpy.data.Image.remove(self.image)

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
        self.is_udim = self.image.tiles is not None

    @classmethod
    def from_blender_image(cls, image: bpy.types.Image, image_format_settings: ImageSettings) -> ImageResource:
        return cls.create(
            width=image.size[0],
            height=image.size[1],
            name=image.name,
            filepath=image.filepath_raw,
            colorspace=image.colorspace_settings.name,
            alpha=image.alpha_mode == "ALPHA",
            float_buffer=image.is_float,
            is_udim=image.source == "TILED",
            image_format_settings=image_format_settings,
        )

    @classmethod
    def from_artifact(cls, artifact: OutputArtifact) -> ImageResource:
        if artifact.name in bpy.data.images and artifact.path == bpy.data.images[artifact.name].filepath_raw:
            image = bpy.data.images[artifact.name]
            return cls.from_blender_image(image, artifact.output_settings.image)

        image = artifact.load_image()

        return image

    def __repr__(self) -> str:
        result = ""
        result += f"{self.name} : {self.filepath}\nwidth = {self.width}\nheight = {self.height}"
        return result
