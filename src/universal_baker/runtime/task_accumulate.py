from __future__ import annotations

from dataclasses import dataclass

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..accumulators.base import AccumulatorBase
    from ..properties.bake_group import UBK_BakeGroup

from ..constant import LOG
from .task import Task
from ..runtime.settings_accumulate import AccumulateSettings
from ..logger.event import ScopeState
from ..logger_bake_middleware.bake_summary import BakeStatus, EventCategory


@dataclass(slots=True, frozen=True)
class AccumulateTask(Task):
    baker_name: str
    baker_uuid: str
    accumulator: AccumulatorBase
    settings: AccumulateSettings
    image_name: str

    @property
    def bake_group(self) -> UBK_BakeGroup | None:
        from ..core.controller import BakeController

        return BakeController.get_bake_group_from_uuid(self.bake_group_uuid)

    @property
    def accumulator_id(self) -> str:
        return self.accumulator.id

    @property
    def output_name(self) -> str:
        assert self.bake_group is not None
        return f"{self.bake_group.name}_{self.image_name}"

    @property
    def accumulator_name(self) -> str:
        return self.accumulator.name

    def __repr__(self) -> str:
        result = f"ACCUMULATOR_{self.accumulator_id:30} | {self.output_name:30} "
        return result

    def notify_finished(self, time_elapsed: float) -> None:
        with LOG.scope("Accumulating"):
            LOG.info(
                message=f"{self.__repr__()} succeeded",
                category=EventCategory.ACCUMULATE,
                scope_state=ScopeState.EXIT,
                scope_duration=time_elapsed,
                data={
                    "status": BakeStatus.SUCCESS,
                    "image": self.image_name,
                },
            )

    def notify_failed(self, time_elapsed: float, error: str) -> None:
        with LOG.scope("Accumulating"):
            LOG.error(
                message=f"{self.accumulator.name.capitalize()} failed",
                category=EventCategory.ACCUMULATE,
                scope_state=ScopeState.EXIT,
                scope_duration=time_elapsed,
                data={
                    "status": BakeStatus.FAIL,
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
