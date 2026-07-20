from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import bpy
from ..runtime.task_pack import PackingTask

from .image import ImageResource
from ..packers.channels import Channel


@dataclass(slots=True)
class PackResource:
    """
    This object stores both the Blender Image and all metadata
    required by the packing pipeline.
    """

    output_image: ImageResource | None = None

    red_uuid: str | None = None
    green_uuid: str | None = None
    blue_uuid: str | None = None
    alpha_uuid: str | None = None

    red_channel_mapping: Channel = Channel.R
    green_channel_mapping: Channel = Channel.G
    blue_channel_mapping: Channel = Channel.B
    alpha_channel_mapping: Channel = Channel.A

    def __init__(self, task: PackingTask) -> None:
        if task.red:
            self.red_uuid = task.red.source_map_uuid
            self.red_channel_mapping = task.red.source_channel
        if task.green:
            self.green_uuid = task.green.source_map_uuid
            self.green_channel_mapping = task.green.source_channel
        if task.blue:
            self.blue_uuid = task.blue.source_map_uuid
            self.blue_channel_mapping = task.blue.source_channel
        if task.alpha:
            self.alpha_uuid = task.alpha.source_map_uuid
            self.alpha_channel_mapping = task.alpha.source_channel

    @property
    def red_resource(self) -> ImageResource | None:
        if self.red_uuid is None:
            return None

        return self.get_resource_from_uuid(self.red_uuid)

    @property
    def green_resource(self) -> ImageResource | None:
        if self.green_uuid is None:
            return None

        return self.get_resource_from_uuid(self.green_uuid)

    @property
    def blue_resource(self) -> ImageResource | None:
        if self.blue_uuid is None:
            return None

        return self.get_resource_from_uuid(self.blue_uuid)

    @property
    def alpha_resource(self) -> ImageResource | None:
        if self.alpha_uuid is None:
            return None

        return self.get_resource_from_uuid(self.alpha_uuid)

    def get_resource_from_uuid(self, uuid: str) -> ImageResource | None:
        from ..core.controller import BakeController

        return BakeController.get_resource_from_uuid(uuid)
