from __future__ import annotations

from dataclasses import dataclass

from ..packers.packer_base import Packer

from .task import Task
from ..packers.channels import Channel


@dataclass(slots=True)
class PackingChannel:
    source_map_uuid: str
    source_channel: Channel
    destination_channel: Channel


@dataclass(slots=True, frozen=True)
class PackingTask(Task):
    packer: Packer
    output_name: str
    settings: object

    red: PackingChannel | None
    green: PackingChannel | None
    blue: PackingChannel | None
    alpha: PackingChannel | None

    def __repr__(self) -> str:
        result = "R : "
        if self.red is None:
            result += "Empty"
        else:
            result += self.red.source_channel + " : " + self.red.destination_channel
        result += " | "
        result = " G : "
        if self.green is None:
            result += "Empty"
        else:
            result += self.green.source_channel + " : " + self.green.destination_channel
        result += " | "
        result = " B : "
        if self.blue is None:
            result += "Empty"
        else:
            result += self.blue.source_channel + " : " + self.blue.destination_channel
        result += " | "
        result = " A : "
        if self.alpha is None:
            result += "Empty"
        else:
            result += self.alpha.source_channel + " : " + self.alpha.destination_channel

        return result
