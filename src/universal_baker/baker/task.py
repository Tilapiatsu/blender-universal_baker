from __future__ import annotations

from dataclasses import dataclass

import bpy

from ..maps.base import BaseBaker


@dataclass(slots=True, frozen=True)
class BakeTask:
    """Immutable description of one bake operation."""

    target: bpy.types.Object
    sources: list[bpy.types.Object]

    baker_id: str

    output: object

    selected_to_active: bool = False
    cage_object: bpy.types.Object | None = None
    cage_extrusion: float = 0.0

    @property
    def object_name(self) -> str:
        return self.target.name

    # @property
    # def baker_id(self) -> str:
    #     return self.baker.id
    #
    # @property
    # def baker_name(self) -> str:
    #     return self.baker.label
