from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from ..constant import LOG
from ..enum.output_stage import OutputStage
from ..services.image_pack import ImageServicePack
from ..services.artifact_service import ArtifactService

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..runtime.context_pack import PackContext
    from ..runtime.task import Task

LOG_SCOPE = "Packing"


class PackerBase(ABC):
    """Abstract baker interface.

    Every Packer is responsible for preparing Blender,
    executing one Pack, then restoring the scene.
    """

    id: str = ""
    name: str = ""
    description: str = ""
    icon: str = "NODE_COMPOSITING"

    def poll(self, task: Task) -> bool:
        """Whether this packer can execute this task."""
        return True

    @abstractmethod
    def execute(self, ctx: PackContext) -> None:
        """Prepare, bake and cleanup all at once."""
        with LOG.scope(LOG_SCOPE):
            LOG.info(f"{str(ctx.task)}")

            self.prepare(ctx)
            self.pack(ctx)
            self.update_pack(ctx)
            self.create_artifact(ctx)
            self.cleanup(ctx)
            self.export_file(ctx)

    @abstractmethod
    def prepare(self, ctx: PackContext) -> None:
        """Prepare Blender before packing."""

    @abstractmethod
    def pack(self, ctx: PackContext) -> None:
        """Execute the Packing."""

    @abstractmethod
    def update_pack(self, ctx: PackContext) -> None:
        from ..core.controller import BakeController

        packer = BakeController.get_paker_from_uuid(ctx.task.uuid)

        if packer is None:
            return

        packer.image = ctx.image.image

    @abstractmethod
    def cleanup(self, ctx: PackContext) -> None:
        """Restore Blender."""
        ctx.image.reset()

    @abstractmethod
    def create_artifact(self, ctx: PackContext) -> None:
        LOG.debug("Creating Artifact ...")
        dependencies = []

        if ctx.pack_resource is not None:
            dependencies = ctx.pack_resource.uuids

        artifact = ArtifactService.register(
            runtime=ctx.session.runtime,
            project=ctx.project,
            artifact_type=OutputStage.PACK,
            bake_group_uuid=ctx.task.bake_group_uuid,
            name=ctx.task.output_name,
            target_object_uuid="",
            producer_uuid=ctx.task.uuid,
            dependencies=dependencies,
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
    def export_file(self, ctx: PackContext):
        """Save Pack to disk."""
        if ctx.task.output_context.output_settings.path.export_file:
            ImageServicePack.save(ctx.image)
