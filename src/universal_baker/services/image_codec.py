from __future__ import annotations

from pathlib import Path

import bpy
from universal_baker.constant import LOG

from ..resources.image_buffer import ImageBuffer
from ..runtime.settings_output import OutputSettings
from ..runtime.output_artifact import OutputArtifact
from ..runtime.tile_set import TileSet


class ImageCodec:
    """
    Converts ImageBuffers to image files and vice-versa.

    This class intentionally ignores UDIM, Artifacts and the runtime.
    It only knows how to serialize one image.
    """

    TMP_NAME = "__UBK_CODEC__"

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    @classmethod
    def save(
        cls,
        filepath: str | Path,
        buffer: ImageBuffer,
        output_settings: OutputSettings,
    ) -> None:
        LOG.debug(f"Saving {filepath}")
        image = cls._create_image(buffer, output_settings)
        try:
            cls._configure_image(
                image,
                filepath=filepath,
                output_settings=output_settings,
            )

            image.save()

        finally:
            bpy.data.images.remove(image)

    @classmethod
    def load(cls, filepath: str | Path) -> ImageBuffer:
        LOG.debug(f"Loading {filepath}")

        image = bpy.data.images.load(str(filepath), check_existing=False)

        try:
            return ImageBuffer.from_blender_image(image)

        finally:
            bpy.data.images.remove(image)

    @classmethod
    def _create_image(cls, buffer: ImageBuffer, output_settings: OutputSettings) -> bpy.types.Image:
        image = bpy.data.images.new(
            cls.TMP_NAME,
            width=buffer.width,
            height=buffer.height,
            alpha=output_settings.image.alpha,
            float_buffer=output_settings.image.float_buffer,
        )

        image.pixels.foreach_set(buffer.flat_pixels)
        image.update()
        return image

    @classmethod
    def _configure_image(
        cls,
        image: bpy.types.Image,
        *,
        filepath: str | Path,
        output_settings: OutputSettings,
    ) -> None:
        LOG.debug("Configuring image")
        image.filepath_raw = str(filepath)
        image.file_format = output_settings.image.file_format
        settings = image
        settings.colorspace_settings.name = output_settings.color.colorspace
        image.save_render

    @classmethod
    def export_tiles(cls, artifact: OutputArtifact, tiles: TileSet, output_settings: OutputSettings):
        for tile, buffer in tiles.tile_buffers:
            cls.save(artifact.image.tile_path(tile), buffer, output_settings)

    @classmethod
    def import_tiles(cls, artifact: OutputArtifact) -> TileSet:
        tile_set = TileSet()

        for t in artifact.image.files():
            tile_set.add_tile(t.tile, cls.load(t.path))

        return tile_set
