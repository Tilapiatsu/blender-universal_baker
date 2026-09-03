from __future__ import annotations

import bpy

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..properties.bake_group import UBK_BakeGroup
    from ..properties.baker import UBK_Baker
    from ..properties.packer import UBK_Packer

from ..output.output_tokens import get_variables
from ..runtime.output_context import OutputContext
from ..runtime.settings_output import OutputSettings, PathSettings
from ..runtime.settings_image import (
    ImageSettings,
    ColorManagementSettings,
)


class OutputSettingsResolver:
    @classmethod
    def resolve(cls, global_settings, override_settings=None) -> OutputSettings:

        if override_settings is None:
            settings = global_settings

        else:
            settings = override_settings

        return OutputSettings(
            image=ImageSettings(
                cineon_black=settings.file_format_settings.cineon_black,
                cineon_gamma=settings.file_format_settings.cineon_gamma,
                cineon_white=settings.file_format_settings.cineon_white,
                color_depth=settings.file_format_settings.color_depth,
                color_management=settings.file_format_settings.color_management,
                color_mode=settings.file_format_settings.color_mode,
                compression=settings.file_format_settings.compression,
                exr_codec=settings.file_format_settings.exr_codec,
                file_format=settings.file_format_settings.file_format,
                has_linear_colorspace=settings.file_format_settings.has_linear_colorspace,
                jpeg2k_codec=settings.file_format_settings.jpeg2k_codec,
                media_type=settings.file_format_settings.media_type,
                quality=settings.file_format_settings.quality,
                tiff_codec=settings.file_format_settings.tiff_codec,
                use_cineon_log=settings.file_format_settings.use_cineon_log,
                use_exr_interleave=settings.file_format_settings.use_exr_interleave,
                use_jpeg2k_cinema_48=settings.file_format_settings.use_jpeg2k_cinema_48,
                use_jpeg2k_cinema_preset=settings.file_format_settings.use_jpeg2k_cinema_preset,
                use_jpeg2k_ycc=settings.file_format_settings.use_jpeg2k_ycc,
                use_preview=settings.file_format_settings.use_preview,
                views_format=settings.file_format_settings.views_format,
            ),
            color=ColorManagementSettings(
                override_colorspace=settings.output_settings.override_colorspace,
                colorspace=settings.output_settings.colorspace,
            ),
            path=PathSettings(
                width=settings.output_settings.width,
                height=settings.output_settings.height,
                colorspace=settings.output_settings.colorspace,
                export_file=settings.output_settings.export_file,
                output_path=settings.output_settings.output_path,
                filename_template=settings.output_settings.filename_template,
            ),
        )


class OutputContextResolver:
    @classmethod
    def resolve(
        cls,
        group_name: str,
        scene: bpy.context.Scene,
        global_settings,
        baker: UBK_Baker | None = None,
        packer: UBK_Packer | None = None,
        override_settings=None,
    ) -> OutputContext:
        output_settings = OutputSettingsResolver.resolve(global_settings, override_settings)

        image_name = "Image"
        if baker is not None:
            image_name = baker.image_name
        elif packer is not None:
            image_name = packer.image_name

        output_context = OutputContext(
            directory_template=output_settings.path.output_path,
            filename_template=output_settings.path.filename_template,
            extension=output_settings.image.file_format,
            variables=get_variables(
                bake_group_name=group_name,
                baker=baker,
                packer=packer,
                image_name=image_name,
                scene=scene,
                extension=output_settings.image.file_format,
            ),
            output_settings=output_settings,
        )
        return output_context


class UvOwnershipOutputContextResolver:
    @classmethod
    def resolve(
        cls,
        group: UBK_BakeGroup,
        scene: bpy.context.Scene,
        global_settings,
    ) -> OutputContext:

        max_output_settings: OutputSettings | None = None

        for baker in group.bakers:
            curr_output_settings = OutputSettingsResolver.resolve(
                global_settings=global_settings,
                override_settings=baker.settings if baker.override_settings else None,
            )

            if max_output_settings is None:
                max_output_settings = curr_output_settings
                continue

            if (
                curr_output_settings.path.width > max_output_settings.path.width
                or curr_output_settings.path.height > max_output_settings.path.height
            ):
                max_output_settings = curr_output_settings

        assert max_output_settings is not None
        output_settings = max_output_settings

        output_context = OutputContext(
            directory_template=output_settings.path.output_path,
            filename_template=output_settings.path.filename_template,
            extension=output_settings.image.file_format,
            variables=get_variables(
                bake_group_name=group.name,
                baker=None,
                packer=None,
                image_name="UVOwnership",
                scene=scene,
                extension=output_settings.image.file_format,
            ),
            output_settings=output_settings,
        )
        return output_context
