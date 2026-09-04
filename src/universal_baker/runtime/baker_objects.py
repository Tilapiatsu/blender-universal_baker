from __future__ import annotations

from dataclasses import dataclass

import bpy


@dataclass(slots=True)
class BakerObjects:
    target: bpy.types.Object
    sources: list[bpy.types.Object]

    @property
    def selected_to_active(self):
        return len(self.sources) > 0

    @property
    def baker_material_objects(self):
        if self.selected_to_active:
            return self.sources
        else:
            return [self.target]
