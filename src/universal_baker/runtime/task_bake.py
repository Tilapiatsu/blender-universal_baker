from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import bpy

from typing import TYPE_CHECKING


from .task import Task

if TYPE_CHECKING:
    from ..bakers.base import BakerBase
    from ..properties.bake_group import UBK_BakeGroup

from ..runtime.settings_bake import BakeSettings


@dataclass(slots=True, frozen=True)
class BakeTask(Task):
    bake_group: UBK_BakeGroup
    target: bpy.types.Object
    sources: tuple[bpy.types.Object]
    baker: BakerBase
    settings: BakeSettings
    image_name: str
    # output_path: Path
    # cage_object: bpy.types.Object | None

    @property
    def object_name(self) -> str:
        return self.target.name

    @property
    def baker_id(self) -> str:
        return self.baker.id

    @property
    def output_name(self) -> str:
        return f"{self.object_name}_{self.baker_id.lower()}"

    @property
    def baker_name(self) -> str:
        return self.baker.name

    @property
    def selected_to_active(self) -> bool:
        return len(self.sources) > 0

    def __repr__(self) -> str:
        result = f"{self.object_name:100} | BAKER_{self.baker_id}"
        return result
