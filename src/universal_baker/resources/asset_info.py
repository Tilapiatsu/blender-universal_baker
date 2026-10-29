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
    extrusion: float
    skew_image: bpy.types.Image


@dataclass(slots=True, frozen=True)
class SourcesInfo(AssetInfo):
    max_ray_distance: float
    shader: str


@dataclass(slots=True, frozen=True)
class CageSkewInfo(AssetInfo):
    uvmap: str | None
    skew_image: bpy.types.Image | None
    precision: float | None
    offset: float | None
    offset_group: str | None
    optimize_resample: bool | None
