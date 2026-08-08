from __future__ import annotations

import bpy

from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty,
    EnumProperty,
    IntProperty,
    CollectionProperty,
    BoolProperty,
    FloatProperty,
)
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..runtime.settings_output import OutputSettings

from ..enum.channels import CHANNEL_ITEMS


ARTIFACT_TYPES = [
    ("BAKE", "Bake", ""),
    ("ACCUMULATED", "Accumulated", ""),
    ("PACK", "Packed", ""),
]


class UBK_ArtifactDependency(PropertyGroup):
    """
    Stores a dependency to another artifact.
    """

    uuid: StringProperty()


class UBK_ProducerUUID(PropertyGroup):
    uuid: StringProperty()


class UBK_ChannelMapping(PropertyGroup):
    channel: EnumProperty(
        name="SRC",
        items=CHANNEL_ITEMS,
        default="R",
    )


class UBK_UDIMTile(PropertyGroup):
    number: IntProperty()


class UBK_Artifact(PropertyGroup):
    """
    Persistent description of one generated output.

    This PropertyGroup is intentionally lightweight.
    Image pixels are never stored here.
    """

    uuid: StringProperty()
    name: StringProperty()
    type: EnumProperty(
        items=ARTIFACT_TYPES,
        default="BAKE",
    )

    bake_group_uuid: StringProperty()
    producer_uuid: StringProperty()
    target_object_uuid: StringProperty()
    output_path: StringProperty()
    filename_template: StringProperty()
    filename: StringProperty()
    absolute_path: StringProperty()
    extension: StringProperty()
    width: IntProperty()
    height: IntProperty()
    channels: IntProperty(
        default=4,
    )
    export_file: BoolProperty()
    colorspace: StringProperty()
    checksum: StringProperty()
    created: StringProperty()
    image_layout: StringProperty()
    udim_tiles: CollectionProperty(type=UBK_UDIMTile)
    dependencies: CollectionProperty(
        type=UBK_ArtifactDependency,
    )
    dependencies_mapping: CollectionProperty(type=UBK_ChannelMapping)

    # ImageSettings
    cineon_black: IntProperty()
    cineon_gamma: FloatProperty()
    cineon_white: IntProperty()
    color_depth: StringProperty()
    color_management: StringProperty()
    color_mode: StringProperty()
    compression: IntProperty()
    exr_codec: StringProperty()
    file_format: StringProperty()
    has_linear_colorspace: BoolProperty()
    jpeg2k_codec: StringProperty()
    media_type: StringProperty()
    quality: IntProperty()
    tiff_codec: StringProperty()
    use_cineon_log: BoolProperty()
    use_exr_interleave: BoolProperty()
    use_jpeg2k_cinema_48: BoolProperty()
    use_jpeg2k_cinema_preset: BoolProperty()
    use_jpeg2k_ycc: BoolProperty()
    use_preview: BoolProperty()
    views_format: StringProperty()

    def get_udim_tiles(self) -> tuple[int, ...]:
        tiles = []
        for tile in self.udim_tiles:
            tiles.append(tile.number)

        return tuple(tiles)

    def feed_from_output_settings(self, output_settings: OutputSettings):
        self.width = output_settings.path.width
        self.height = output_settings.path.height
        self.colorspace = output_settings.path.colorspace
        self.output_path = output_settings.path.output_path
        self.filename_template = output_settings.path.filename_template
        self.filename = Path(output_settings.path.output_path).name
        self.extension = Path(output_settings.path.output_path).suffix.lower()
        self.export_file = output_settings.path.export_file

        # ImageSettings
        self.cineon_black = output_settings.image.cineon_black
        self.cineon_gamma = output_settings.image.cineon_gamma
        self.cineon_white = output_settings.image.cineon_white
        self.color_depth = output_settings.image.color_depth
        self.color_management = output_settings.image.color_management
        self.color_mode = output_settings.image.color_mode
        self.compression = output_settings.image.compression
        self.exr_codec = output_settings.image.exr_codec
        self.file_format = output_settings.image.file_format
        self.has_linear_colorspace = output_settings.image.has_linear_colorspace
        self.jpeg2k_codec = output_settings.image.jpeg2k_codec
        self.media_type = output_settings.image.media_type
        self.quality = output_settings.image.quality
        self.tiff_codec = output_settings.image.tiff_codec
        self.use_cineon_log = output_settings.image.use_cineon_log
        self.use_exr_interleave = output_settings.image.use_exr_interleave
        self.use_jpeg2k_cinema_48 = output_settings.image.use_jpeg2k_cinema_48
        self.use_jpeg2k_cinema_preset = output_settings.image.use_jpeg2k_cinema_preset
        self.use_jpeg2k_ycc = output_settings.image.use_jpeg2k_ycc
        self.use_preview = output_settings.image.use_preview
        self.views_format = output_settings.image.views_format

    def get_output_settings(self) -> OutputSettings:
        from ..runtime.settings_image import ImageSettings, ColorManagementSettings
        from ..runtime.settings_output import OutputSettings, PathSettings

        color = ColorManagementSettings(self.colorspace)
        path = PathSettings(
            width=self.width,
            height=self.height,
            colorspace=self.colorspace,
            export_file=self.export_file,
            output_path=self.output_path,
            filename_template=self.filename_template,
        )
        image = ImageSettings(
            cineon_black=self.cineon_black,
            cineon_gamma=self.cineon_gamma,
            cineon_white=self.cineon_white,
            color_depth=self.color_depth,
            color_management=self.color_depth,
            color_mode=self.color_mode,
            compression=self.compression,
            exr_codec=self.exr_codec,
            file_format=self.file_format,
            has_linear_colorspace=self.has_linear_colorspace,
            jpeg2k_codec=self.jpeg2k_codec,
            media_type=self.media_type,
            quality=self.quality,
            tiff_codec=self.tiff_codec,
            use_cineon_log=self.use_cineon_log,
            use_exr_interleave=self.use_exr_interleave,
            use_jpeg2k_cinema_48=self.use_jpeg2k_cinema_48,
            use_jpeg2k_cinema_preset=self.use_jpeg2k_cinema_preset,
            use_jpeg2k_ycc=self.use_jpeg2k_ycc,
            use_preview=self.use_preview,
            views_format=self.views_format,
        )

        output = OutputSettings(
            image=image,
            color=color,
            path=path,
        )

        return output


classes = (
    UBK_ChannelMapping,
    UBK_ArtifactDependency,
    UBK_ProducerUUID,
    UBK_UDIMTile,
    UBK_Artifact,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
