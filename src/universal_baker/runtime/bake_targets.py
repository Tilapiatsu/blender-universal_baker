from __future__ import annotations

from dataclasses import dataclass

import bpy


@dataclass(slots=True, frozen=True)
class BakeTargets:
    uuid: str
    target: bpy.types.Object
    sources: list[bpy.types.Object]

    @property
    def have_source(self) -> bool:
        return len(self.sources) > 0

    @property
    def bake_targets(self) -> list[bpy.types.Object]:
        if self.have_source:
            return self.sources
        else:
            return [self.target]
