from __future__ import annotations
from abc import abstractmethod

from universal_baker.resources.pack import ImageResource

from ..runtime.context import PackContext
from .packer_base import PackerBase

from ..runtime.image_buffer import ImageBuffer
from ..services.image_pack import ImageServicePack
from ..services.image_io import ImageIOService
from .channels import Channel

try:
    import numpy as np
except ImportError:
    np = None


class PackerInternal(PackerBase):
    """
    Blender-independent channel packing utility.

    Operates exclusively on ImageBuffer instances.
    """

    id: str = "INTERNAL"
    label: str = "Pack Internal"
    description: str = "Pack rendered bake using blender"

    def execute(self, ctx: PackContext) -> None:
        return super().execute(ctx)

    def export_file(self, ctx: PackContext):
        """Save Pack to disk."""
        return super().export_file(ctx)

    def prepare(self, ctx: PackContext) -> None:
        """Prepare Blender before packing."""
        task = ctx.task
        ctx.pack_resource = ImageServicePack.create_pack_resource(task)

        ctx.red_resource = ctx.pack_resource.red_resource
        ctx.green_resource = ctx.pack_resource.green_resource
        ctx.blue_resource = ctx.pack_resource.blue_resource
        ctx.alpha_resource = ctx.pack_resource.alpha_resource

        resources: tuple[ImageResource, ...] = tuple([])

        if ctx.red_resource is not None and task.red and task.red.enabled:
            ctx.pack_red = True
            resources += (ctx.red_resource,)
        if ctx.green_resource is not None and task.green and task.green.enabled:
            ctx.pack_green = True
            resources += (ctx.green_resource,)
        if ctx.blue_resource is not None and task.blue and task.blue.enabled:
            ctx.pack_blue = True
            resources += (ctx.blue_resource,)
        if ctx.alpha_resource is not None and task.alpha and task.alpha.enabled:
            ctx.pack_alpha = True
            resources += (ctx.alpha_resource,)

        if not len(resources):
            print("No Image Resource Found")
            return

        ImageIOService.ensure_image_sizes(*resources)

        ctx.output_buffer = self.create_buffer(resources[0].width, resources[0].height)

    def pack(self, ctx: PackContext) -> None:
        """Execute the packing."""

        if ctx.output_buffer:
            if (
                ctx.pack_red
                and ctx.red_resource
                and ctx.pack_resource
                and ctx.pack_resource.red_channel_mapping
                and ctx.red_resource.exists
            ):
                image_buffer = ImageIOService.read(ctx.red_resource)
                self.copy_channel(ctx.output_buffer, ctx.pack_resource.red_channel_mapping, image_buffer, Channel.R)
            if (
                ctx.pack_green
                and ctx.green_resource
                and ctx.pack_resource
                and ctx.pack_resource.green_channel_mapping
                and ctx.green_resource.exists
            ):
                image_buffer = ImageIOService.read(ctx.green_resource)
                self.copy_channel(ctx.output_buffer, ctx.pack_resource.green_channel_mapping, image_buffer, Channel.G)
            if (
                ctx.pack_blue
                and ctx.blue_resource
                and ctx.pack_resource
                and ctx.pack_resource.blue_channel_mapping
                and ctx.blue_resource.exists
            ):
                image_buffer = ImageIOService.read(ctx.blue_resource)
                self.copy_channel(ctx.output_buffer, ctx.pack_resource.blue_channel_mapping, image_buffer, Channel.B)
            if (
                ctx.pack_alpha
                and ctx.alpha_resource
                and ctx.pack_resource
                and ctx.pack_resource.alpha_channel_mapping
                and ctx.alpha_resource.exists
            ):
                image_buffer = ImageIOService.read(ctx.alpha_resource)
                self.copy_channel(ctx.output_buffer, ctx.pack_resource.alpha_channel_mapping, image_buffer, Channel.A)

            ctx.image = ImageIOService.acquire(ctx.image, ctx.task)
            ImageIOService.write(ctx.image, ctx.output_buffer)

        else:
            print("Missing output buffer")

    def cleanup(self, ctx: PackContext) -> None:
        """Restore Blender."""
        if ctx.red_resource and ctx.red_resource.exists and ctx.red_resource.is_copy:
            ImageServicePack.remove(ctx.red_resource.image)

        if ctx.green_resource and ctx.green_resource.exists and ctx.green_resource.is_copy:
            ImageServicePack.remove(ctx.green_resource.image)

        if ctx.blue_resource and ctx.blue_resource.exists and ctx.blue_resource.is_copy:
            ImageServicePack.remove(ctx.blue_resource.image)

        if ctx.alpha_resource and ctx.alpha_resource.exists and ctx.alpha_resource.is_copy:
            ImageServicePack.remove(ctx.alpha_resource.image)

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
    def create_buffer(width: int, height: int) -> ImageBuffer:
        """Create an Image Buffer with the given width and height"""
        return ImageBuffer.empty(width, height)

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
