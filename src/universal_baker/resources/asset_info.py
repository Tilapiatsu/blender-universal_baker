from __future__ import annotations

from dataclasses import dataclass

import bpy


@dataclass(slots=True, frozen=True)
class AssetInfo:
    pass


@dataclass(slots=True, frozen=True)
class CageInfo(AssetInfo):
    uvmap: str
    cage_object: bpy.types.Object
    target_object: bpy.types.Object
    offset: tuple[float, float, float]
