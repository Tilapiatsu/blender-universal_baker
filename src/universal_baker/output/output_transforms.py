from __future__ import annotations

import bpy

from ..core.registry_transform import registry_transform
from ..constant import SAFE_CHR


def make_safe(value: str) -> str:
    return value.replace(" ", SAFE_CHR).replace("/", SAFE_CHR).replace("\\", SAFE_CHR)


def register():
    registry_transform.register(
        "lower",
        str.lower,
    )
    registry_transform.register(
        "upper",
        str.upper,
    )
    registry_transform.register(
        "title",
        str.title,
    )
    registry_transform.register(
        "capitalize",
        str.capitalize,
    )
    registry_transform.register(
        "safe",
        make_safe,
    )


def unregister():
    pass
