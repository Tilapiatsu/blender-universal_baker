from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import bpy

from .task import Task
from ..bakers.base import BaseBaker
from ..runtime.settings_bake import BakeSettings
from ..runtime.settings_cage import CageSettings


@dataclass(slots=True, frozen=True)
class BakeTask(Task):
    target: bpy.types.Object
    sources: tuple[bpy.types.Object]
    baker: BaseBaker
    settings_bake: BakeSettings
    image_name: str
    # output_path: Path
    cage_object: bpy.types.Object | None
    settings_cage: CageSettings

    @property
    def object_name(self) -> str:
        return self.target.name

    @property
    def baker_id(self) -> str:
        return self.baker.id

    @property
    def baker_name(self) -> str:
        return self.baker.label

    @property
    def selected_to_active(self) -> bool:
        return len(self.sources) > 0

    def __repr__(self) -> str:
        result = f"{self.object_name:100} | BAKER_{self.baker_id}"
        return result
