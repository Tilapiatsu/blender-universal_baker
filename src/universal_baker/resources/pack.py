from __future__ import annotations

from dataclasses import dataclass, field


from ..services.output_provider import OutputProvider
from ..runtime.task_pack import PackingTask
from ..runtime.tile_set import TileSet

from .image import ImageResource
from ..enum.channels import Channel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..runtime.context_pack import PackContext


@dataclass(slots=True)
class PackResource:
    """
    This object stores both the Blender Image and all metadata
    required by the packing pipeline.
    """

    ctx: PackContext
    provider: OutputProvider

    output_image: ImageResource | None = None

    bake_group_uuid: str = field(default_factory=str)
    red_uuid: str | None = None
    green_uuid: str | None = None
    blue_uuid: str | None = None
    alpha_uuid: str | None = None

    red_channel_mapping: Channel = Channel.R
    green_channel_mapping: Channel = Channel.G
    blue_channel_mapping: Channel = Channel.B
    alpha_channel_mapping: Channel = Channel.A

    def __init__(self, task: PackingTask, ctx: PackContext) -> None:
        self.ctx = ctx
        self.bake_group_uuid = task.bake_group_uuid
        self.provider = ctx.session.runtime.provider
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
    def red_buffer(self) -> TileSet | None:
        if self.red_uuid is None:
            return None

        return self.get_tile_set_from_baker_uuid(self.red_uuid)

    @property
    def green_buffer(self) -> TileSet | None:
        if self.green_uuid is None:
            return None

        return self.get_tile_set_from_baker_uuid(self.green_uuid)

    @property
    def blue_buffer(self) -> TileSet | None:
        if self.blue_uuid is None:
            return None

        return self.get_tile_set_from_baker_uuid(self.blue_uuid)

    @property
    def alpha_buffer(self) -> TileSet | None:
        if self.alpha_uuid is None:
            return None

        return self.get_tile_set_from_baker_uuid(self.alpha_uuid)

    @property
    def uuids(self) -> list[str]:
        uuids = []

        if self.red_uuid is not None:
            uuids.append(self.red_uuid)
        if self.green_uuid is not None:
            uuids.append(self.green_uuid)
        if self.blue_uuid is not None:
            uuids.append(self.blue_uuid)
        if self.alpha_uuid is not None:
            uuids.append(self.alpha_uuid)

        return uuids

    def get_tile_set_from_baker_uuid(self, uuid: str) -> TileSet | None:
        return self.provider.get_image(self.bake_group_uuid, uuid)
