from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import bpy

from ..bakers.base import BaseBaker
from ..runtime.bake_settings import BakeSettings
from ..runtime.cage_settings import CageSettings


@dataclass(slots=True, frozen=True)
class BakeTask:
    target: bpy.types.Object
    sources: tuple[bpy.types.Object]
    baker: BaseBaker
    bake_settings: BakeSettings
    image_name: str
    # output_path: Path
    cage_object: bpy.types.Object | None
    cage_settings: CageSettings

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
