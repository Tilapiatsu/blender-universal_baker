from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..packers.packer_base import PackerBase

from .task import Task
from .settings_pack import PackSettings
from ..packers.channels import Channel


@dataclass(slots=True)
class PackingChannel:
    enabled: bool
    source_map_uuid: str
    source_map_name: str
    source_channel: Channel
    destination_channel: Channel


@dataclass(slots=True, frozen=True)
class PackingTask(Task):
    packer: PackerBase
    settings: PackSettings
    image_name: str

    red: PackingChannel | None
    green: PackingChannel | None
    blue: PackingChannel | None
    alpha: PackingChannel | None

    @property
    def output_name(self) -> str:
        return self.image_name

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

        return f"{result:100} | PACKER_{self.packer.id}"
