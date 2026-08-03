from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING


from ..constant import LOG
from ..enum.output_stage import OutputStage
from ..services.image_bake import ImageServiceBake
from ..services.artifact_service import ArtifactService
from ..core.accumulator import ImageAccumulator
from ..core.registry_compositor import registry_compositor
from ..logger_bake_middleware.bake_summary import BakeStatus, EventCategory
from ..services.image_io import ImageIOService

if TYPE_CHECKING:
    from ..runtime.context_accumulate import AccumulateContext
    from ..runtime.task import Task

LOG_SCOPE = "Accumulating"


class AccumulatorBase(ABC):
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

    def poll(self, task: Task) -> bool:
        """Whether this baker can execute this task."""
        return True

    @abstractmethod
    def execute(self, ctx: AccumulateContext) -> None:
        """Prepare, bake and cleanup all at once."""
        with LOG.scope(LOG_SCOPE):
            LOG.info(f"{str(ctx.task)}")

            self.prepare(ctx)
            self.accumulate(ctx)
            self.update_baker(ctx)
            # self.create_output(ctx)
            self.create_artifact(ctx)
            self.export_file(ctx)
            self.cleanup(ctx)

    @abstractmethod
    def prepare(self, ctx: AccumulateContext) -> None:
        """Prepare Blender before baking."""
        LOG.debug("Preparing Scene ...")

    @abstractmethod
    def accumulate(self, ctx: AccumulateContext) -> None:
        """Execute the bake."""
        LOG.debug("Accumulating ...")
        images = ctx.get_input_images()
        if not len(images):
            LOG.error(
                "No Image found",
                category=EventCategory.ACCUMULATE,
                data={
                    "status": BakeStatus.FAIL,
                },
            )

        accumulator = ImageAccumulator(
            width=images[0].size[0],
            height=images[0].size[1],
            name=f"Accumulated_{ctx.image.name}",
        )

        for image in images:
            buffer = ImageIOService.read_image(image)
            accumulator.accumulate(buffer, registry_compositor[self.id])

        ctx.output_buffer = accumulator.result()
        ImageIOService.write(ctx.image, ctx.output_buffer)

    @abstractmethod
    def cleanup(self, ctx: AccumulateContext) -> None:
        """Restore Blender."""
        LOG.debug("Restoring ...")
        ctx.image.reset()

    @abstractmethod
    def update_baker(self, ctx: AccumulateContext) -> None:
        LOG.debug("Update Baker ...")
        from ..core.controller import BakeController

        baker = BakeController.get_baker_from_uuid(ctx.task.baker_uuid)

        if baker is None:
            LOG.warning("Baker not found")
            return

        baker.accumulated_image = ctx.image.image

    @abstractmethod
    def create_artifact(self, ctx: AccumulateContext) -> None:
        LOG.debug("Creating Artifact ...")
        ArtifactService.register(
            runtime=ctx.session.runtime,
            project=ctx.project,
            artifact_type=OutputStage.ACCUMULATED,
            name=ctx.task.output_name,
            bake_group_uuid=ctx.task.bake_group_uuid,
            target_object_uuid="",
            producer_uuid=ctx.task.uuid,
            filepath=ctx.image.filepath,
            width=ctx.image.width,
            height=ctx.image.height,
            channels=ctx.image.channels,
            color_space=ctx.image.colorspace,
            file_format=ctx.output_settings.image.file_format,
        )

    @abstractmethod
    def export_file(self, ctx: AccumulateContext) -> None:
        """Save Bake to disk."""
        LOG.debug("Saving File to Disk ...")
        if ctx.task.output_context.output_settings.path.export_file:
            ImageServiceBake.save(ctx.image)
