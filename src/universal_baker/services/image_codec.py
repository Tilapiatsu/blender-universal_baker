from __future__ import annotations

from pathlib import Path

import bpy

from ..constant import LOG
from ..resources.image_buffer import ImageBuffer
from ..runtime.color_management_info import ColorManagementInfo
from ..runtime.output_artifact import OutputArtifact
from ..runtime.settings_image import ColorManagementSettings
from ..runtime.settings_output import OutputSettings
from ..runtime.tile_set import TileSet
from .view_transform_override import ViewTransformOverride

LOG_SCOPE = "Image Codec"


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
        filepath: Path,
        buffer: ImageBuffer,
        output_settings: OutputSettings,
        color_management_info: ColorManagementInfo | None = None,
    ) -> None:
        image = cls._create_image(buffer, output_settings)
        try:
            cls._configure_image(
                image,
                filepath=filepath,
                output_settings=output_settings,
            )

            if color_management_info is not None and color_management_info.apply_view_transform:
                with ViewTransformOverride.override(bpy.context.scene, color_management_info):
                    LOG.debug(f"Saving file as render : {filepath}")
                    image.save_render(str(filepath), scene=bpy.context.scene)
            else:
                image.save()
                LOG.debug(f"Saving file : {filepath}")

        finally:
            bpy.data.images.remove(image)

    @classmethod
    def load(cls, filepath: Path, colorspace: ColorManagementSettings) -> ImageBuffer | None:
        if filepath.exists():
            LOG.debug(f"Loading {filepath}")
            image = bpy.data.images.load(str(filepath), check_existing=False)
            image.colorspace_settings.name = colorspace.colorspace

            try:
                return ImageBuffer.from_blender_image(image)

            finally:
                bpy.data.images.remove(image)
        else:
            return None

    @classmethod
    def _create_image(cls, buffer: ImageBuffer, output_settings: OutputSettings) -> bpy.types.Image:
        image = bpy.data.images.new(
            cls.TMP_NAME,
            width=buffer.width,
            height=buffer.height,
            alpha=output_settings.image.alpha,
            float_buffer=output_settings.image.float_buffer,
        )

        buffer.write_to_blender_image(image)
        image.update()
        image.pack()
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
        # settings.save_as_render = True

    @classmethod
    def export_tiles(cls, artifact: OutputArtifact, tiles: TileSet, output_settings: OutputSettings):
        with LOG.scope(LOG_SCOPE):
            for tile, buffer in tiles.tile_buffers:
                cls.save(
                    artifact.image.tile_path(tile),
                    buffer,
                    output_settings,
                    artifact.color_management_info,
                )
                tiles.set_dirty(tile, False)

    @classmethod
    def import_tiles(cls, artifact: OutputArtifact) -> TileSet:
        tile_set = TileSet()

        for t in artifact.image.files():
            with LOG.scope(LOG_SCOPE):
                buffer = cls.load(t.path, artifact.output_settings.color)
            if buffer is not None:
                tile_set.add_tile(t.tile, buffer)
            else:
                with LOG.scope(LOG_SCOPE):
                    LOG.debug("Create Empty Tile")
                    tile_set.add_empty_tile(
                        t.tile,
                        (
                            artifact.output_settings.path.width,
                            artifact.output_settings.path.height,
                        ),
                    )
                    cls.save(
                        artifact.image.tile_path(t.tile),
                        tile_set[t.tile],
                        artifact.output_settings,
                        artifact.color_management_info,
                    )

        return tile_set
