from __future__ import annotations

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
                colorspace=settings.output_settings.colorspace,
            ),
            path=PathSettings(
                resolution_x=settings.output_settings.resolution_x,
                resolution_y=settings.output_settings.resolution_y,
                colorspace=settings.output_settings.colorspace,
                export_file=settings.output_settings.export_file,
                output_path=settings.output_settings.output_path,
                filename_template=settings.output_settings.filename_template,
            ),
        )
