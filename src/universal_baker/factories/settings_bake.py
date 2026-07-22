from __future__ import annotations

from ..runtime.settings_bake import (
    BakeSettings,
    BakeRenderSettings,
    SamplingSettings,
)


class BakeSettingsResolver:
    @classmethod
    def resolve(cls, global_settings, override_settings=None) -> BakeSettings:

        if override_settings is None:
            settings = global_settings

        else:
            settings = override_settings

        return BakeSettings(
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
        )
