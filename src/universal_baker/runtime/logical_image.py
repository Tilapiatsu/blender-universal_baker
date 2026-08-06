from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Generator

import bpy

from ..enum.image_layout import ImageLayout


@dataclass(slots=True)
class ArtifactFile:
    tile: int
    path: Path


@dataclass(frozen=True)
class LogicalImage:
    layout: ImageLayout
    _path: Path
    tiles: tuple[int, ...]

    @property
    def path(self) -> Path:
        """Returns the resolved path of the file"""
        return Path(bpy.path.abspath(self._path))

    def exists(self) -> bool:
        """Returns true if the file exists on disk"""
        return self.path.exists()

    @property
    def is_udim(self) -> bool:
        return self.layout == "UDIM"

    def tile_path(self, tile: int) -> Path:
        if self.layout == ImageLayout.SINGLE:
            return self.path

        return Path(str(self.path).replace("<UDIM>", str(tile)))

    def files(self) -> Generator[ArtifactFile]:
        if self.layout == ImageLayout.SINGLE:
            yield ArtifactFile(tile=1001, path=self.path)

        else:
            for tile in self.tiles:
                yield ArtifactFile(tile=tile, path=self.tile_path(tile))
