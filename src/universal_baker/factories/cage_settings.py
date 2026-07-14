from __future__ import annotations

from ..runtime.cage_settings import (
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
            extrusion=settings.extrusion,
            max_ray_distance=settings.max_ray_distance,
        )
