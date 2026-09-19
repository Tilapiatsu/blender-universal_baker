from __future__ import annotations

from dataclasses import dataclass, field

import bpy


@dataclass(slots=True, frozen=True)
class BakeObjects:
    target_object: bpy.types.Object
    cage_object: bpy.types.Object | None
    cage_hidden: bool = False
    is_cage_generated: bool = False
    source_objects: list[bpy.types.Object] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        if not self.selected_to_active and self.target_object is not None:
            return True

        return self.cage_object is not None and len(self.target_object.data.vertices) == len(
            self.cage_object.data.vertices
        )

    @property
    def selected_to_active(self) -> bool:
        return len(self.source_objects) > 0 if self.source_objects is not None else False

    @property
    def baker_material_objects(self) -> list[bpy.types.Object]:
        if self.selected_to_active:
            return self.source_objects
        else:
            return [self.target_object]
