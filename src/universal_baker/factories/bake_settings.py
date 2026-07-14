from __future__ import annotations

from ..runtime.bake_settings import (
    BakeSettings,
    ImageSettings,
    BakeRenderSettings,
    SamplingSettings,
    ColorManagementSettings,
)


class BakeSettingsResolver:
    @classmethod
    def resolve(cls, global_settings, override_settings=None) -> BakeSettings:

        if override_settings is None:
            settings = global_settings

        elif override_settings.inherit:
            settings = global_settings

        else:
            settings = override_settings

        return BakeSettings(
            image=ImageSettings(
                width=settings.resolution_x,
                height=settings.resolution_y,
                file_format=settings.file_format,
                color_depth=settings.color_depth,
                alpha=settings.alpha,
            ),
            bake=BakeRenderSettings(
                margin=settings.margin,
                margin_type=settings.margin_type,
            ),
            sampling=SamplingSettings(
                adaptive_sampling=settings.adaptive_sampling,
                samples=settings.samples,
                noise_threshold=settings.noise_threshold,
                min_samples=settings.min_samples,
                max_samples=settings.max_samples,
                denoise=settings.denoise,
            ),
            color=ColorManagementSettings(
                colorspace=settings.colorspace,
            ),
        )
