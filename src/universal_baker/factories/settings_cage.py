from __future__ import annotations

from ..properties.settings_cage import UBK_CageSettings
from ..runtime.settings_cage import (
    CageSettings,
)


class CageSettingsResolver:
    @classmethod
    def resolve(
        cls,
        global_settings: UBK_CageSettings,
        override_settings: UBK_CageSettings | None = None,
    ) -> CageSettings:

        if override_settings is None or override_settings.inherit:
            settings = global_settings

        else:
            settings = override_settings

        return CageSettings(
            cage_object_name=settings.cage_object.name if settings.cage_object is not None else None,
            mode=settings.cage_mode,
            cage_extrusion=settings.cage_extrusion,
            max_ray_distance=settings.max_ray_distance,
            extrusion_group_name=settings.extrusion_group,
            skew_map_name=settings.skew_map.name if settings.skew_map is not None else None,
        )
