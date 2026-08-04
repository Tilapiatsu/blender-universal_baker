from __future__ import annotations

from dataclasses import dataclass

import bpy

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..bakers.base import BakerBase
    from ..properties.bake_group import UBK_BakeGroup
    from ..properties.object import UBK_TargetObject

from ..constant import LOG
from .task import Task
from ..runtime.settings_bake import BakeSettings
from ..logger.event import ScopeState
from ..logger_bake_middleware.bake_summary import BakeStatus, EventCategory


@dataclass(slots=True, frozen=True)
class BakeTask(Task):
    id: str
    target_object_uuid: str
    sources: tuple[bpy.types.Object]
    baker: BakerBase
    settings: BakeSettings
    image_name: str
    uv_layer: str

    has_multiple_targets: bool = False
    # output_path: Path
    # cage_object: bpy.types.Object | None

    @property
    def bake_group(self) -> UBK_BakeGroup | None:
        from ..core.controller import BakeController

        return BakeController.get_bake_group_from_uuid(self.bake_group_uuid)

    @property
    def target(self) -> UBK_TargetObject:
        from ..core.controller import BakeController

        return BakeController.get_target_object_from_uuid(self.target_object_uuid)

    @property
    def object_name(self) -> str:
        return self.target.object.name

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
        result = f"BAKER_{self.baker_id} | {self.object_name:100} "
        return result

    def notify_finished(self, time_elapsed: float) -> None:
        with LOG.scope("Baking"):
            LOG.info(
                message=f"{self.baker_id.capitalize()} succeeded",
                category=EventCategory.BAKE,
                scope_state=ScopeState.EXIT,
                scope_duration=time_elapsed,
                data={
                    "status": BakeStatus.SUCCESS,
                    "object": self.object_name,
                    "image": self.image_name,
                },
            )

    def notify_failed(self, time_elapsed: float, error: str) -> None:
        with LOG.scope("Baking"):
            LOG.error(
                message=f"{self.baker_id.capitalize()} failed",
                category=EventCategory.BAKE,
                scope_state=ScopeState.EXIT,
                scope_duration=time_elapsed,
                data={
                    "status": BakeStatus.FAIL,
                    "object": self.object_name,
                    "image": self.image_name,
                },
            )
            LOG.error(
                message=error,
                category=EventCategory.BAKE,
                data={
                    "status": BakeStatus.FAIL,
                },
            )
