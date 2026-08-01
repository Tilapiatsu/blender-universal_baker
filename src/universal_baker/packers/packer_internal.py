from __future__ import annotations

import numpy as np

from ..constant import LOG
from ..logger_bake_middleware.bake_summary import BakeStatus
from ..runtime.context_pack import PackContext
from .base import PackerBase

from ..core.registry_packer import registry_packer
from ..runtime.image_buffer import ImageBuffer
from ..services.image_pack import ImageServicePack
from ..services.image_io import ImageIOService
from ..enum.channels import Channel


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
        ctx.pack_resource = ImageServicePack.create_pack_resource(task, ctx)

        ctx.red_buffer = ctx.pack_resource.red_buffer
        ctx.green_buffer = ctx.pack_resource.green_buffer
        ctx.blue_buffer = ctx.pack_resource.blue_buffer
        ctx.alpha_buffer = ctx.pack_resource.alpha_buffer

        buffers: tuple[ImageBuffer, ...] = tuple([])

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

        if not len(buffers):
            with LOG.scope(self.id.capitalize()):
                LOG.warning("No Image Resource Found")
            return

        ctx.output_buffer = self.create_buffer(buffers[0].width, buffers[0].height, ctx.task.image_name)

    def pack(self, ctx: PackContext) -> None:
        """Execute the packing."""

        if ctx.output_buffer:
            if ctx.pack_red and ctx.red_buffer and ctx.pack_resource and ctx.pack_resource.red_channel_mapping:
                self.copy_channel(ctx.output_buffer, ctx.pack_resource.red_channel_mapping, ctx.red_buffer, Channel.R)
            if ctx.pack_green and ctx.green_buffer and ctx.pack_resource and ctx.pack_resource.green_channel_mapping:
                self.copy_channel(
                    ctx.output_buffer, ctx.pack_resource.green_channel_mapping, ctx.green_buffer, Channel.G
                )
            if ctx.pack_blue and ctx.blue_buffer and ctx.pack_resource and ctx.pack_resource.blue_channel_mapping:
                self.copy_channel(ctx.output_buffer, ctx.pack_resource.blue_channel_mapping, ctx.blue_buffer, Channel.B)
            if ctx.pack_alpha and ctx.alpha_buffer and ctx.pack_resource and ctx.pack_resource.alpha_channel_mapping:
                self.copy_channel(
                    ctx.output_buffer, ctx.pack_resource.alpha_channel_mapping, ctx.alpha_buffer, Channel.A
                )

            ctx.image = ImageIOService.acquire(ctx.image, ctx.task)
            ImageIOService.write(ctx.image, ctx.output_buffer)

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
    def validate_same_size(*buffers: ImageBuffer) -> None:
        """Check if the inputed buffers have the same size"""
        if not buffers:
            return

        width = buffers[0].width
        height = buffers[0].height

        for buffer in buffers[1:]:
            if buffer.width != width or buffer.height != height:
                raise ValueError("All images must have identical dimensions.")

    # -------------------------------------------------------------------------
    # Buffer creation
    # -------------------------------------------------------------------------

    @staticmethod
    def create_buffer(width: int, height: int, name: str = "Image") -> ImageBuffer:
        """Create an Image Buffer with the given width and height"""
        return ImageBuffer.empty(width, height, name=name)

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    @classmethod
    def copy_channel(
        cls, destination: ImageBuffer, destination_channel: Channel, source: ImageBuffer, source_channel: Channel
    ) -> None:
        """Copy a channel from source ImageBuffer to a destination ImageBuffer"""
        cls.validate_same_size(destination, source)
        if np is not None:
            cls._copy_numpy(
                destination,
                destination_channel,
                source,
                source_channel,
            )

        else:
            cls._copy_python(
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
        cls, destination: ImageBuffer, destination_channel: Channel, source: ImageBuffer, source_channel: Channel
    ) -> None:
        """Copy a channel from source ImageBuffer to a destination ImageBuffer using numpy"""

        dst = destination.reshape()
        src = source.reshape()

        dst_index = cls._channel_index(destination_channel)
        src_index = cls._channel_index(source_channel)

        dst[..., dst_index] = src[..., src_index]

    # -------------------------------------------------------------------------
    # Pure Python implementation
    # -------------------------------------------------------------------------

    @classmethod
    def _copy_python(
        cls, destination: ImageBuffer, destination_channel: Channel, source: ImageBuffer, source_channel: Channel
    ) -> None:
        """Copy a channel from source ImageBuffer to a destination ImageBuffer using python"""

        dst = destination.pixels
        src = source.pixels

        dst_index = cls._channel_index(destination_channel)
        src_index = cls._channel_index(source_channel)

        for i in range(destination.size):
            base = i * 4

            dst[base + dst_index] = src[base + src_index]

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
