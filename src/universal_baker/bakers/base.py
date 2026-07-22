from __future__ import annotations

from enum import Enum, auto
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..runtime.context import BakeContext
    from ..runtime.task import Task

from ..services.renderer import RendererService
from ..services.image_bake import ImageServiceBake


class BakerColorType(Enum):
    COLOR = auto()
    DATA = auto()
    MASK = auto()
    VECTOR = auto()


class BakerBase(ABC):
    """Abstract baker interface.

    Every baker is responsible for preparing Blender,
    executing one bake, then restoring the scene.

    The executor knows nothing about AO, Curvature,
    Diffuse, etc.
    """

    id: str = ""
    name: str = ""
    description: str = ""
    icon: str = "RENDER_STILL"
    color_type: BakerColorType = BakerColorType.COLOR
    blender_bake_type = "DIFFUSE"

    def poll(self, task: Task) -> bool:
        """Whether this baker can execute this task."""
        return True

    @abstractmethod
    def execute(self, ctx: BakeContext) -> None:
        """Prepare, bake and cleanup all at once."""
        self.prepare(ctx)
        self.bake(ctx)
        self.update_baker(ctx)
        self.export_file(ctx)
        self.cleanup(ctx)

    @abstractmethod
    def prepare(self, ctx: BakeContext) -> None:
        """Prepare Blender before baking."""

    @abstractmethod
    def bake(self, ctx: BakeContext) -> None:
        """Execute the bake."""
        RendererService.execute(ctx)

    @abstractmethod
    def cleanup(self, ctx: BakeContext) -> None:
        """Restore Blender."""

    @abstractmethod
    def update_baker(self, ctx: BakeContext) -> None:
        from ..core.controller import BakeController

        baker = BakeController.get_baker_from_uuid(ctx.task.uuid)

        if baker is None:
            return

        baker.image = ctx.image.image

    @abstractmethod
    def export_file(self, ctx: BakeContext):
        """Save Bake to disk."""
        if ctx.task.output_context.output_settings.path.export_file:
            ImageServiceBake.save(ctx.image)
