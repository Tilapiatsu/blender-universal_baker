from __future__ import annotations

import bpy

from dataclasses import dataclass


@dataclass(slots=True)
class EvaluatedTarget:
    uuid: str
    name: str
    object: bpy.types.Object
    mesh: bpy.types.Mesh
