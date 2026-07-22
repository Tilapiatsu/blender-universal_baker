from __future__ import annotations

from ..runtime.settings_pack import (
    PackSettings,
)


class PackSettingsResolver:
    @classmethod
    def resolve(cls, global_settings, override_settings=None) -> PackSettings:

        if override_settings is None:
            settings = global_settings

        else:
            settings = override_settings

        return PackSettings()
