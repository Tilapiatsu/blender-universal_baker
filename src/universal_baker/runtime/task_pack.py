from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..packers.base import PackerBase
    from ..properties.bake_group import UBK_BakeGroup

from ..constant import LOG
from .task import Task
from .settings_pack import PackSettings
from ..enum.channels import Channel
from ..logger.event import ScopeState
from ..logger_bake_middleware.bake_summary import BakeStatus, EventCategory


@dataclass(slots=True)
class PackingChannel:
    enabled: bool
    source_map_uuid: str
    source_map_name: str
    source_channel: Channel
    destination_channel: Channel


@dataclass(slots=True, frozen=True)
class PackingTask(Task):
    id: str
    packer: PackerBase
    settings: PackSettings
    image_name: str

    red: PackingChannel | None
    green: PackingChannel | None
    blue: PackingChannel | None
    alpha: PackingChannel | None

    @property
    def bake_group(self) -> UBK_BakeGroup | None:
        from ..core.controller import BakeController

        return BakeController.get_bake_group_from_uuid(self.bake_group_uuid)

    @property
    def output_name(self) -> str:
        return self.image_name

    @property
    def packer_name(self) -> str:
        return self.packer.name

    def __repr__(self) -> str:
        result = ""
        if self.red is None:
            result += "R -> Empty"
        else:
            result += self.red.source_map_name + "_" + self.red.source_channel + " -> " + self.red.destination_channel
        result += " | "

        if self.green is None:
            result += "G -> Empty"
        else:
            result += (
                self.green.source_map_name + "_" + self.green.source_channel + " -> " + self.green.destination_channel
            )
        result += " | "

        if self.blue is None:
            result += "B -> Empty"
        else:
            result += (
                self.blue.source_map_name + "_" + self.blue.source_channel + " -> " + self.blue.destination_channel
            )
        result += " | "

        if self.alpha is None:
            result += "A -> Empty"
        else:
            result += (
                self.alpha.source_map_name + "_" + self.alpha.source_channel + " -> " + self.alpha.destination_channel
            )

        return f"PACKER_{self.packer.id} | {result:50}"

    def notify_finished(self, time_elapsed: float) -> None:
        with LOG.scope("Packing"):
            LOG.info(
                message=f"{self.__repr__()} succeeded",
                category=EventCategory.PACK,
                scope_state=ScopeState.EXIT,
                scope_duration=time_elapsed,
                data={
                    "status": BakeStatus.SUCCESS,
                    "image": self.image_name,
                },
            )

    def notify_failed(self, time_elapsed: float, error: str) -> None:
        with LOG.scope("Packing"):
            LOG.error(
                message=f"{self.packer.name} failed",
                category=EventCategory.PACK,
                scope_state=ScopeState.EXIT,
                scope_duration=time_elapsed,
                data={
                    "status": BakeStatus.FAIL,
                    "image": self.image_name,
                },
            )
            LOG.error(message=error, category="BAKE")
