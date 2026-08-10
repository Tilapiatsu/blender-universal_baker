from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING


from ..constant import LOG
from ..enum.output_stage import OutputStage
from ..services.artifact_service import ArtifactService
from ..core.maskers import ImageMasker
from ..core.registry_compositor import registry_compositor
from ..logger_bake_middleware.bake_summary import BakeStatus, EventCategory

if TYPE_CHECKING:
    from ..runtime.context_mask import MaskContext
    from ..runtime.task import Task

LOG_SCOPE = "Masking"


class MaskerBase(ABC):
    """Abstract Masker interface.

    Every masker is responsible for preparing Blender,
    executing one masking, then restoring the scene.
    """

    id: str = ""
    name: str = ""
    description: str = ""
    icon: str = "MOD_MASK"

    def poll(self, task: Task) -> bool:
        """Whether this baker can execute this task."""
        return True

    @abstractmethod
    def execute(self, ctx: MaskContext) -> None:
        """Prepare, bake and cleanup all at once."""
        with LOG.scope(LOG_SCOPE):
            LOG.info(f"{str(ctx.task)}")

            self.prepare(ctx)
            # self.create_artifact(ctx)
            self.masking(ctx)
            self.update_baker(ctx)
            self.export_file(ctx)
            self.cleanup(ctx)

    @abstractmethod
    def prepare(self, ctx: MaskContext) -> None:
        """Prepare Blender before baking."""
        LOG.debug("Preparing Scene ...")
        inputs = ctx.get_input_image_handles(ctx.session.runtime.outputs)
        if not len(inputs):
            LOG.error(
                "No Image found",
                category=EventCategory.MASK,
                data={
                    "status": BakeStatus.FAIL,
                },
            )

        LOG.debug(f"{len(inputs)} input(s) found")

        ctx.inputs = inputs

    @abstractmethod
    def masking(self, ctx: MaskContext) -> None:
        """Execute the Accumulation."""
        LOG.debug("Masking ...")

        if ctx.inputs is None:
            LOG.error("Inputs are not defined")
            return

        for image in ctx.inputs:
            if not ctx.mask.contains(image.tileset):
                LOG.debug(f"Skipping {image.artifact.name}")
                continue
            ImageMasker.apply_mask(image, ctx.mask, registry_compositor[self.id])
            image.image()
            image.reload()

    @abstractmethod
    def cleanup(self, ctx: MaskContext) -> None:
        """Restore Blender."""
        LOG.debug("Restoring ...")
        ctx.image.reset()

    @abstractmethod
    def update_baker(self, ctx: MaskContext) -> None:
        LOG.debug("Update Baker ...")
        from ..core.controller import BakeController

        baker = BakeController.get_baker_from_uuid(ctx.task.baker_uuid)

        if baker is None:
            LOG.warning("Baker not found")
            return

        baker.accumulated_image = ctx.image.image

    @abstractmethod
    def create_artifact(self, ctx: MaskContext) -> None:
        LOG.debug("Creating Artifact ...")
        artifact = ArtifactService.register(
            runtime=ctx.session.runtime,
            project=ctx.project,
            artifact_type=OutputStage.MASKED,
            name=ctx.task.output_name,
            bake_group_uuid=ctx.task.bake_group_uuid,
            target_object_uuid="",
            producer_uuid=ctx.task.uuid,
            image_layout=ctx.task.uv_layout.image_layout,
            uv_layout=ctx.task.uv_layout,
            absolute_path=ctx.task.absolute_filepath,
            output_settings=ctx.output_settings,
        )

        if artifact is None:
            LOG.error("Artifact creation Failed")
            return

        LOG.info(str(artifact))

        ctx.output = ctx.session.runtime.outputs.get(artifact)
        if ctx.output is None:
            return

        ctx.task.result.set_tileset(ctx.output.tileset, clear=True)

    @abstractmethod
    def export_file(self, ctx: MaskContext) -> None:
        """Save Bake to disk."""
        LOG.debug("Saving File to Disk ...")
        if ctx.task.output_context.output_settings.path.export_file and ctx.inputs is not None:
            for input in ctx.inputs:
                input.save()
