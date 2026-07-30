from __future__ import annotations

from enum import Enum, auto
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING


from ..constant import LOG
from ..services.image_io import ImageIOService
from ..services.renderer import RendererService
from ..services.image_bake import ImageServiceBake
from ..runtime.output_bake import OutputBake

if TYPE_CHECKING:
    from ..runtime.context import BakeContext
    from ..runtime.task import Task

LOG_SCOPE = "Baking"


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
        with LOG.scope(LOG_SCOPE):
            LOG.info(f"{str(ctx.task)}")

            self.prepare(ctx)
            self.bake(ctx)
            self.update_baker(ctx)
            self.create_output(ctx)
            self.export_file(ctx)
            self.cleanup(ctx)

    @abstractmethod
    def prepare(self, ctx: BakeContext) -> None:
        """Prepare Blender before baking."""
        LOG.debug("Preparing Scene ...")

    @abstractmethod
    def bake(self, ctx: BakeContext) -> None:
        """Execute the bake."""
        LOG.debug("Baking ...")
        RendererService.execute(ctx)

    @abstractmethod
    def cleanup(self, ctx: BakeContext) -> None:
        LOG.debug("Restoring ...")
        """Restore Blender."""

    @abstractmethod
    def update_baker(self, ctx: BakeContext) -> None:
        LOG.debug("Upate Baker ...")
        from ..core.controller import BakeController

        baker = BakeController.get_baker_from_uuid(ctx.task.uuid)

        if baker is None:
            return

        image = baker.images.add()
        image.object_name = ctx.target.name
        image.image = ctx.image.image
        image.target_object_uuid = ctx.task.target.uuid

        target = BakeController.get_target_object_from_uuid(ctx.task.target.uuid)
        if target is None:
            return

        target.image = ctx.image.image

    @abstractmethod
    def create_output(self, ctx: BakeContext):
        LOG.debug("Creating Output ...")
        buffer = ImageIOService.read(ctx.image)

        output = OutputBake.create(
            uuid=ctx.task.uuid,
            name=ctx.image.name,
            image=buffer,
            bake_group=ctx.task.bake_group,
            baker=ctx.task.baker,
        )

        ctx.session.runtime.outputs.add(output)
        ctx.session.runtime.provider.invalidate(ctx.task.bake_group.uuid, ctx.task.uuid)

    @abstractmethod
    def export_file(self, ctx: BakeContext):
        """Save Bake to disk."""
        LOG.debug("Creating File ...")
        if ctx.task.output_context.output_settings.path.export_file:
            ImageServiceBake.save(ctx.image)
