from __future__ import annotations

from ..runtime.settings_cage import (
    CageSettings,
)


class CageSettingsResolver:
    @classmethod
    def resolve(cls, global_settings, override_settings=None) -> CageSettings:

        if override_settings is None:
            settings = global_settings

        elif override_settings.inherit:
            settings = global_settings

        else:
            settings = override_settings

        return CageSettings(
            mode=settings.mode,
            cage_extrusion=settings.cage_extrusion,
            max_ray_distance=settings.max_ray_distance,
            extrusion_group=settings.extrusion_group,
            skew_map=settings.skew_map.name,
        )
