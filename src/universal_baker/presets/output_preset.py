from __future__ import annotations

from dataclasses import dataclass

import bpy


@dataclass(slots=True)
class OutputPreset:
    name: str
    node: bpy.types.CompositorNodeOutputFile

    def __init__(self, name: str, node: bpy.types.CompositorNodeOutputFile) -> None:
        self.name = name
        self.node = node
        node.name = name
        node.label = name
        node.format.media_type = "IMAGE"

    @property
    def format(self) -> bpy.types.ImageFormatSettings:
        return self.node.format
