from __future__ import annotations

from enum import Enum, auto
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

from ..constant import LOG
from ..enum.output_stage import OutputStage
from ..services.image_io import ImageIOService
from ..services.renderer import RendererService
from ..services.image_bake import ImageServiceBake
from ..runtime.output_bake import OutputBake
from ..services.artifact_service import ArtifactService
from ..services.material import MaterialService

if TYPE_CHECKING:
    from ..runtime.context_bake import BakeContext
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
    accumulator_id = "ALPHA_OVER"

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
            # self.create_output(ctx)
            self.create_artifact(ctx)
            self.export_file(ctx)
            self.cleanup(ctx)

    @abstractmethod
    def prepare(self, ctx: BakeContext) -> None:
        """Prepare Blender before baking."""
        LOG.debug("Preparing Scene ...")
        if ctx.task.has_multiple_targets:
            ctx.image = ImageServiceBake.acquire(ctx.image, ctx.task, ctx.task.object_name, "object_buffers")
        else:
            ctx.image = ImageServiceBake.acquire(ctx.image, ctx.task)

        MaterialService.prepare_target(ctx)

    @abstractmethod
    def bake(self, ctx: BakeContext) -> None:
        """Execute the bake."""
        LOG.debug("Baking ...")
        RendererService.execute(ctx)

    @abstractmethod
    def cleanup(self, ctx: BakeContext) -> None:
        LOG.debug("Restoring ...")
        """Restore Blender."""
        ctx.image.reset()

    @abstractmethod
    def update_baker(self, ctx: BakeContext) -> None:
        LOG.debug("Update Baker ...")
        from ..core.controller import BakeController

        baker = BakeController.get_baker_from_uuid(ctx.task.uuid)

        if baker is None:
            return

        if ctx.target.name not in baker.images:
            image = baker.images.add()
        else:
            image = baker.images[ctx.target.name]

        image.name = ctx.target.name
        image.image = ctx.image.image
        image.target_object_uuid = ctx.task.target.uuid

        target = BakeController.get_target_object_from_uuid(ctx.task.target.uuid)
        if target is None:
            return

        target.image = ctx.image.image

        if not ctx.task.has_multiple_targets:
            baker.accumulated_image = ctx.image.image

    @abstractmethod
    def create_output(self, ctx: BakeContext) -> None:
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
        ctx.session.runtime.provider.invalidate(ctx.task.bake_group_uuid, ctx.task.uuid)

    @abstractmethod
    def create_artifact(self, ctx: BakeContext) -> None:
        ArtifactService.register(
            runtime=ctx.session.runtime,
            project=ctx.project,
            artifact_type=OutputStage.BAKE,
            bake_group_uuid=ctx.task.bake_group_uuid,
            target_object_uuid=ctx.task.target_object_uuid,
            producer_uuid=ctx.task.uuid,
            filepath=ctx.image.filepath,
            width=ctx.image.width,
            height=ctx.image.height,
            channels=ctx.image.channels,
            color_space=ctx.image.colorspace,
            file_format=ctx.output_settings.image.file_format,
        )

    @abstractmethod
    def export_file(self, ctx: BakeContext) -> None:
        """Save Bake to disk."""
        LOG.debug("Creating File ...")
        if ctx.task.output_context.output_settings.path.export_file:
            ImageServiceBake.save(ctx.image)
