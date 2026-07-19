from __future__ import annotations
from abc import abstractmethod

from ..runtime.context import PackContext
from .packer_base import PackerBase

from ..runtime.image_buffer import ImageBuffer
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

    def prepare(self, ctx: PackContext) -> None:
        """Prepare Blender before packing."""
        # TODO : Prepare and run the pack
        task = ctx.task
        ImageIOService.ensure_image_sizes()
        self.output_buffer = self.create_buffer(256, 256)

    def pack(self, ctx: PackContext) -> None:
        """Execute the packing."""

    def cleanup(self, ctx: PackContext) -> None:
        """Restore Blender."""

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
        cls,
        destination: ImageBuffer,
        destination_channel: Channel,
        source: ImageBuffer,
        source_channel: Channel,
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
    def fill_channel(
        cls,
        destination: ImageBuffer,
        destination_channel: Channel,
        value: float,
    ) -> None:
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
        cls,
        destination: ImageBuffer,
        destination_channel: Channel,
        source: ImageBuffer,
        source_channel: Channel,
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
        cls,
        destination: ImageBuffer,
        destination_channel: Channel,
        source: ImageBuffer,
        source_channel: Channel,
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
