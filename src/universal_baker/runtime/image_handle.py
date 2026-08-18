from __future__ import annotations

from dataclasses import dataclass, field

from typing import Iterator

from .bake_group import BakeGroup


from ..constant import LOG
from .tile_set import TileSet
from .settings_output import OutputSettings
from ..resources.image import ImageResource
from ..resources.image_buffer import ImageBuffer
from ..services.image_codec import ImageCodec
from .output_artifact import OutputArtifact

LOG_SCOPE = "Image Handle"


@dataclass(slots=True)
class ImageHandle:
    """
    Runtime representation of one logical image.

    An ImageHandle may represent either:

        - One regular image
        - One UDIM image

    The caller never has to know which.

    The handle lazily loads buffers, creates Blender images
    when requested, and saves modified buffers back to disk.

    Orchestrates those three representations, performing lazy loading, caching, saving, invalidation, and synchronization.
    """

    uuid: str
    _artifact: OutputArtifact
    _output_settings: OutputSettings
    _resource: ImageResource = field(default_factory=ImageResource)
    _tiles: TileSet = field(default_factory=TileSet)

    # ------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------

    def __init__(self, artifact: OutputArtifact):
        self._artifact = artifact
        self._output_settings = artifact.output_settings
        self._tiles = TileSet()
        self._resource = ImageResource()
        self.uuid = artifact.uuid

    # ------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------

    @property
    def artifact(self) -> OutputArtifact:
        return self._artifact

    @property
    def is_loaded(self) -> bool:
        return not self._tiles.is_empty

    @property
    def is_udim(self) -> bool:
        return self._artifact.is_udim

    @property
    def bake_group(self) -> BakeGroup:
        return self._artifact.bake_group

    @property
    def producer_uuid(self) -> str:
        return self._artifact.producer_uuid

    @property
    def target_object_uuid(self) -> str:
        return self._artifact.target_object_uuid

    @property
    def is_dirty(self) -> bool:
        return self._tiles.is_dirty

    # ------------------------------------------------------------
    # Tile access
    # ------------------------------------------------------------

    @property
    def tileset(self) -> TileSet:
        LOG.debug("Fetching TileSet")
        self._ensure_loaded()
        return self._tiles

    def tiles(self) -> tuple[int, ...]:
        """
        Return every available tile number.

        Loads them if necessary.
        """

        self._ensure_loaded()

        return self._tiles.tiles

    def overlaps(self, tileset: TileSet) -> bool:
        return self._tiles.overlaps(tileset)

    def has_tile(self, tile: int) -> bool:
        self._ensure_loaded()
        return tile in self._tiles

    def buffer(self, tile: int = 1001) -> ImageBuffer:
        """
        Return one tile buffer.
        """
        self._ensure_loaded()
        return self._tiles[tile]

    def set_buffer(self, tile: int, buffer: ImageBuffer) -> None:
        self._ensure_loaded()
        self._tiles.add_tile(tile, buffer, override=True)

    def set_empty_buffer(self, tile: int) -> None:
        self._ensure_loaded()
        self._tiles.add_empty_tile(
            tile,
            (
                self._output_settings.path.width,
                self._output_settings.path.height,
            ),
            override=True,
        )

    def set_tileset(self, tileset: TileSet) -> None:
        self._tiles = tileset

    def set_dirty(self, dirty: bool) -> None:
        for tile in self._tiles.tiles:
            self._tiles.set_dirty(tile, dirty)

    def buffers(self) -> Iterator[tuple[int, ImageBuffer]]:
        self._ensure_loaded()
        yield from self._tiles.tile_buffers

    # ------------------------------------------------------------
    # Blender image
    # ------------------------------------------------------------

    def image(self) -> ImageResource:
        """
        Return a Blender image.

        Creates or reloads it if necessary.
        """
        if self.is_dirty:
            LOG.debug("Handle is dirty")
            self.save()

        if not self._resource.created:
            self._resource = ImageResource.from_artifact(self._artifact)

        return self._resource

    # ------------------------------------------------------------
    # Disk
    # ------------------------------------------------------------

    def save(self):
        with LOG.scope(LOG_SCOPE):
            self._ensure_loaded()

            ImageCodec.export_tiles(
                artifact=self._artifact,
                tiles=self._tiles,
                output_settings=self._output_settings,
            )

            self._resource.reload()

    def reload(self):
        """
        Discard cached buffers and reload them.
        """
        self._tiles.clear()
        self._ensure_loaded()
        self._resource.reload()

    def invalidate(self):
        """
        Free runtime cache.
        """
        self._tiles.clear()

    # ------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------

    def _ensure_loaded(self):
        if not self._tiles.is_empty:
            LOG.warning("TileSet is already loaded")
            return

        self._tiles = ImageCodec.import_tiles(
            self._artifact,
        )

    def __iter__(self):
        self._ensure_loaded()
        return iter(self._tiles.items())

    def clear(self):
        self._tiles.clear()

    @classmethod
    def from_artifact(cls, artifact: OutputArtifact):
        return cls(artifact)
