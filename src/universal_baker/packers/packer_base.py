from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..runtime.context import PackContext
    from ..runtime.task import Task


class PackerBase(ABC):
    """Abstract baker interface.

    Every Packer is responsible for preparing Blender,
    executing one Pack, then restoring the scene.
    """

    id: str = ""
    label: str = ""
    description: str = ""
    icon: str = "NODE_COMPOSITING"

    def poll(self, task: Task) -> bool:
        """Whether this packer can execute this task."""
        return True

    @abstractmethod
    def execute(self, ctx: PackContext) -> None:
        """Prepare, bake and cleanup all at once."""
        self.prepare(ctx)
        self.pack(ctx)
        self.cleanup(ctx)

    @abstractmethod
    def prepare(self, ctx: PackContext) -> None:
        """Prepare Blender before packing."""

    @abstractmethod
    def pack(self, ctx: PackContext) -> None:
        """Execute the Packing."""

    @abstractmethod
    def cleanup(self, ctx: PackContext) -> None:
        """Restore Blender."""
