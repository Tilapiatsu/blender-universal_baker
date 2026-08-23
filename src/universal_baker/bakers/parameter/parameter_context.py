from __future__ import annotations

from dataclasses import dataclass

import bpy


@dataclass
class ParameterContext:
    """
    Objects used while resolving ParameterBindings.

    These are runtime references and must never be persisted.
    """

    object: bpy.types.Object
    material: bpy.types.Material | None = None
    node_group: bpy.types.NodeGroup | None = None

    scene: bpy.types.Scene | None = None

    # Optional reference to the current baker.
    baker: object | None = None
