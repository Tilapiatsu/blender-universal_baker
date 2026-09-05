from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..properties.baker import UBK_Baker
    from ..properties.object import UBK_TargetObject

from ..constant import LOG
from ..core.output_resolver import OutputResolver
from ..logger.event import ScopeState
from ..logger_bake_middleware.bake_summary import BakeStatus, EventCategory
from ..maskers.base import MaskerBase
from ..runtime.task_ownership_mask import UvOwnershipTask
from .task import Task


@dataclass(slots=True, frozen=True)
class MaskBufferTask(Task):
    uv_ownership_task: UvOwnershipTask
    baker_uuid: str
    target_object_uuid: str
    producer: MaskerBase
    has_multiple_targets: bool

    id: str = "MASK"

    @property
    def output_name(self) -> str:
        return f"{self.uv_ownership_task.name}_{self.producer.name}"

    @property
    def absolute_filepath(self) -> Path:
        file_output = OutputResolver.resolve(
            self.output_context,
            self.uv_layout.image_layout,
            self.uv_ownership_task.name,
            "object_buffers" if self.has_multiple_targets else None,
        )

        return file_output.absolute_path

    @property
    def target(self) -> UBK_TargetObject | None:
        from ..core.controller import BakeController

        target = BakeController.get_target_object_from_uuid(self.target_object_uuid)
        return target

    @property
    def baker(self) -> UBK_Baker | None:
        from ..core.controller import BakeController

        baker = BakeController.get_baker_from_uuid(self.baker_uuid)
        return baker

    @property
    def baker_name(self) -> str:
        return self.baker.baker.capitalize() if self.baker is not None else "UNKOWN_BAKER"

    @property
    def target_name(self) -> str:
        return self.target.object.name if self.target is not None else "UNKOWN_TARGET_OBJECT"

    @property
    def task_name(self) -> str:
        return f"{self.target_name}_{self.baker_name}"

    def notify_finished(self, time_elapsed: float) -> None:
        with LOG.scope("Masking"):
            LOG.info(
                message=f"{self.task_name} succeeded{' ':30}",
                category=EventCategory.BAKE,
                scope_state=ScopeState.EXIT,
                scope_duration=time_elapsed,
                data={
                    "status": BakeStatus.SUCCESS,
                },
            )

    def notify_failed(self, time_elapsed: float, error: str) -> None:
        with LOG.scope("Masking"):
            LOG.error(
                message=f"{self.task_name} failed{' ':30}",
                category=EventCategory.BAKE,
                scope_state=ScopeState.EXIT,
                scope_duration=time_elapsed,
                data={
                    "status": BakeStatus.FAIL,
                },
            )
            LOG.error(
                message=error,
                category=EventCategory.BAKE,
                data={
                    "status": BakeStatus.FAIL,
                },
            )

    def __repr__(self) -> str:
        result = f"MASK_{self.producer.id} | {self.uv_ownership_task.name}"
        return result
