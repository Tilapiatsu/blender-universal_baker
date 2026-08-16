from __future__ import annotations

import numpy as np

from ..constant import LOG
from ..logger_bake_middleware.bake_summary import BakeStatus
from ..runtime.context_pack import PackContext
from .base import PackerBase

from ..core.registry_packer import registry_packer
from ..resources.image_buffer import ImageBuffer
from ..services.image_pack import ImagePackService
from ..enum.channels import Channel
from ..runtime.tile_set import TileSet


class PackerInternal(PackerBase):
    """
    Blender-independent channel packing utility.

    Operates exclusively on ImageBuffer instances.
    """

    id: str = "INTERNAL"
    name: str = "Internal"
    description: str = "Pack rendered bake using blender"

    def execute(self, ctx: PackContext) -> None:
        return super().execute(ctx)

    def export_file(self, ctx: PackContext):
        """Save Pack to disk."""
        return super().export_file(ctx)

    def prepare(self, ctx: PackContext) -> None:
        """Prepare Blender before packing."""
        task = ctx.task
        ctx.pack_resource = ImagePackService.create_pack_resource(task, ctx)

        ctx.red_buffer = ctx.pack_resource.red_buffer
        ctx.green_buffer = ctx.pack_resource.green_buffer
        ctx.blue_buffer = ctx.pack_resource.blue_buffer
        ctx.alpha_buffer = ctx.pack_resource.alpha_buffer

        buffers: tuple[TileSet, ...] = ()

        if ctx.red_buffer is not None and task.red and task.red.enabled:
            ctx.pack_red = True
            buffers += (ctx.red_buffer,)
        if ctx.green_buffer is not None and task.green and task.green.enabled:
            ctx.pack_green = True
            buffers += (ctx.green_buffer,)
        if ctx.blue_buffer is not None and task.blue and task.blue.enabled:
            ctx.pack_blue = True
            buffers += (ctx.blue_buffer,)
        if ctx.alpha_buffer is not None and task.alpha and task.alpha.enabled:
            ctx.pack_alpha = True
            buffers += (ctx.alpha_buffer,)

        if len(buffers) == 0:
            with LOG.scope(self.id.capitalize()):
                LOG.warning("No Image Resource Found")
            return

        LOG.debug(f"{len(buffers)} buffer(s) found")
        # TODO: buffers arrive empty : need to investigate
        for b in buffers:
            print(b.values())
            print(b.keys())
        buffer = buffers[0].values()[0]
        ctx.task.result.set_tileset(
            self.create_tile_set(
                buffer.width,
                buffer.height,
                ctx.task.image_name,
                buffers[0].tiles,
            )
        )

    def pack(self, ctx: PackContext) -> None:
        """Execute the packing."""

        if ctx.task.result:
            if ctx.pack_red and ctx.red_buffer and ctx.pack_resource and ctx.pack_resource.red_channel_mapping:
                self.copy_channels(
                    ctx.task.result,
                    ctx.pack_resource.red_channel_mapping,
                    ctx.red_buffer,
                    Channel.R,
                )
            if ctx.pack_green and ctx.green_buffer and ctx.pack_resource and ctx.pack_resource.green_channel_mapping:
                self.copy_channels(
                    ctx.task.result,
                    ctx.pack_resource.green_channel_mapping,
                    ctx.green_buffer,
                    Channel.G,
                )
            if ctx.pack_blue and ctx.blue_buffer and ctx.pack_resource and ctx.pack_resource.blue_channel_mapping:
                self.copy_channels(
                    ctx.task.result,
                    ctx.pack_resource.blue_channel_mapping,
                    ctx.blue_buffer,
                    Channel.B,
                )
            if ctx.pack_alpha and ctx.alpha_buffer and ctx.pack_resource and ctx.pack_resource.alpha_channel_mapping:
                self.copy_channels(
                    ctx.task.result,
                    ctx.pack_resource.alpha_channel_mapping,
                    ctx.alpha_buffer,
                    Channel.A,
                )

        else:
            with LOG.scope(self.id.capitalize()):
                LOG.error(
                    "Missing output buffer",
                    data={
                        "status": BakeStatus.FAIL,
                    },
                )

    def update_pack(self, ctx: PackContext) -> None:
        return super().update_pack(ctx)

    def create_artifact(self, ctx: PackContext) -> None:
        return super().create_artifact(ctx)

    def cleanup(self, ctx: PackContext) -> None:
        """Restore Blender."""
        # if ctx.red_resource and ctx.red_resource.exists and ctx.red_resource.is_copy:
        #     ImageServicePack.remove(ctx.red_resource.image)
        #
        # if ctx.green_resource and ctx.green_resource.exists and ctx.green_resource.is_copy:
        #     ImageServicePack.remove(ctx.green_resource.image)
        #
        # if ctx.blue_resource and ctx.blue_resource.exists and ctx.blue_resource.is_copy:
        #     ImageServicePack.remove(ctx.blue_resource.image)
        #
        # if ctx.alpha_resource and ctx.alpha_resource.exists and ctx.alpha_resource.is_copy:
        #     ImageServicePack.remove(ctx.alpha_resource.image)
        #

    # -------------------------------------------------------------------------
    # Validation
    # -------------------------------------------------------------------------

    @staticmethod
    def validate_same_size(*buffers: TileSet) -> None:
        """Check if the inputed buffers have the same size"""
        if not buffers:
            return

        ref_width = buffers[0].values()[0].width
        ref_height = buffers[0].values()[0].height

        for ts in buffers:
            for buffer in ts.values():
                width = buffer.width
                height = buffer.height

                if ref_width != width or ref_height != height:
                    raise ValueError("All images must have identical dimensions.")

    @staticmethod
    def validate_same_tilesets(*buffers: TileSet) -> None:
        if not buffers:
            return

        ref_tileset = set(buffers[0].keys())

        for ts in buffers[1:]:
            curr_tileset = set(ts.keys())
            if len(curr_tileset.difference(ref_tileset)) > 0:
                raise ValueError(
                    f"Source and Destination tileset should have the tiles count and id.\nSource : {curr_tileset}\nDestination : {ref_tileset}."
                )

    # -------------------------------------------------------------------------
    # Buffer creation
    # -------------------------------------------------------------------------

    @staticmethod
    def create_tile_set(width: int, height: int, name: str = "Image", tiles: tuple[int, ...] = (1001,)) -> TileSet:
        """Create an Image Buffer with the given width and height"""
        ts = TileSet()

        for t in tiles:
            ts[t] = ImageBuffer.empty(width, height, name=name)

        return ts

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    @classmethod
    def copy_channels(
        cls, destination: TileSet, destination_channel: Channel, source: TileSet, source_channel: Channel
    ) -> None:
        """Copy a channel from source ImageBuffer to a destination ImageBuffer"""
        cls.validate_same_size(destination, source)
        cls.validate_same_tilesets(destination, source)

        LOG.debug(f"Copy {source_channel.value} to {destination_channel.value}")
        cls._copy_numpy(
            destination,
            destination_channel,
            source,
            source_channel,
        )

    @classmethod
    def fill_channel(cls, destination: ImageBuffer, destination_channel: Channel, value: float) -> None:
        """Write a value to the inputed channel of the ImageBuffer"""
        if np is not None:
            pixels = destination.reshape()
            pixels[..., cls._channel_index(destination_channel)] = value
            return

        index = cls._channel_index(destination_channel)
        pixels = destination.pixels

        for i in range(destination.size):
            pixels[i * 4 + index] = value

    # -------------------------------------------------------------------------
    # NumPy implementation
    # -------------------------------------------------------------------------

    @classmethod
    def _copy_numpy(
        cls, destination: TileSet, destination_channel: Channel, source: TileSet, source_channel: Channel
    ) -> None:
        """Copy a channel from source ImageBuffer to a destination ImageBuffer using numpy"""

        for udim in source.keys():
            if udim not in destination.keys():
                raise ValueError(f"Destination don't have {udim} tileset")

            dst = destination[udim].reshape()
            src = source[udim].reshape()

            dst_index = cls._channel_index(destination_channel)
            src_index = cls._channel_index(source_channel)

            dst[..., dst_index] = src[..., src_index]

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _channel_index(channel: Channel) -> int:
        """Get Channel Index based of Channel"""
        if channel == Channel.R:
            return 0

        if channel == Channel.G:
            return 1

        if channel == Channel.B:
            return 2

        if channel == Channel.A:
            return 3

        raise ValueError(f"{channel} is not a single channel.")


classes = (PackerInternal,)


def register():
    for c in classes:
        registry_packer.register(c())


def unregister():
    pass
