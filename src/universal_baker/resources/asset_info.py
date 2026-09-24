from __future__ import annotations

from dataclasses import dataclass

import bpy

"""
AssetInfo dataclasses should contains attributes with name matches the id declared in the asset .blend file.
If the name doesn't match the binding with the parameter jsut cannot work properly
"""


@dataclass(slots=True, frozen=True)
class AssetInfo:
    pass


@dataclass(slots=True, frozen=True)
class CageInfo(AssetInfo):
    uvmap: str
    cage_object: bpy.types.Object
    target_object: bpy.types.Object
    offset: tuple[float, float, float]


@dataclass(slots=True, frozen=True)
class SourcesInfo(AssetInfo):
    max_ray_distance: float
    shader: str
