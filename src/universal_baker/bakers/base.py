from __future__ import annotations
import bpy

from enum import Enum, auto
from abc import ABC
from abc import abstractmethod
from contextlib import contextmanager

from typing import TYPE_CHECKING, Any, Generator


from ..enum.image_colorspace import ImageColorSpace
from ..constant import LOG
from ..runtime.baker_setup import BakerExecution, BakerSetup
from ..enum.output_stage import OutputStage
from ..services.renderer import RendererService
from ..services.image_bake import ImageServiceBake
from ..services.artifact_service import ArtifactService
from ..services.material import MaterialService
from ..services.bake_material import BakeMaterialService

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
    is_custom: bool = False
    colorspace: ImageColorSpace = ImageColorSpace.NON_COLOR

    def poll(self, task: Task) -> bool:
        """Whether this baker can execute this task."""
        return True

    @abstractmethod
    @contextmanager
    def prepare_execution(self, target: bpy.types.Object) -> Generator[BakerExecution, Any, Any]:

        material_setup = BakeMaterialService.prepare(objects=[target])
        baker_setup = BakerSetup(material_setup=material_setup)

        try:
            yield BakerExecution(
                target=target,
                setup=baker_setup,
            )

        finally:
            material_setup.cleanup()

    @abstractmethod
    def configure_preview_material(self, material):
        material.use_nodes = True
        nodes = material.node_tree.nodes
        nodes.clear()

        output = nodes.new("ShaderNodeOutputMaterial")
        shader = nodes.new("ShaderNodeBsdfPrincipled")

        material.node_tree.links.new(
            shader.outputs["BSDF"],
            output.inputs["Surface"],
        )

        output.location.x = shader.location.x + 200

    @abstractmethod
    def execute(self, ctx: BakeContext) -> None:
        """Prepare, bake and cleanup all at once."""
        with LOG.scope(LOG_SCOPE):
            LOG.info(f"{str(ctx.task)}")

            self.prepare(ctx)
            self.bake(ctx)
            self.update_baker(ctx)
            self.export_file(ctx)
            self.create_artifact(ctx)
            self.cleanup(ctx)

    @abstractmethod
    def prepare(self, ctx: BakeContext) -> None:
        """Prepare Blender before baking."""
        LOG.debug("Preparing Scene ...")

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
    def create_artifact(self, ctx: BakeContext) -> None:
        LOG.debug("Creating Artifact ...")

        artifact = ArtifactService.register(
            runtime=ctx.session.runtime,
            project=ctx.project,
            artifact_type=OutputStage.BAKE,
            name=ctx.task.output_name,
            bake_group_uuid=ctx.task.bake_group_uuid,
            target_object_uuid=ctx.task.target_object_uuid,
            producer_uuid=ctx.task.uuid,
            image_layout=ctx.task.uv_layout.image_layout,
            uv_layout=ctx.task.uv_layout,
            absolute_path=ctx.task.absolute_filepath,
            output_settings=ctx.output_settings,
        )

        if artifact is None:
            return

        ctx.output = ctx.session.runtime.outputs.get(artifact)
        if ctx.output is None:
            return

        ctx.task.result.set_tileset(ctx.output.tileset, clear=True)
        ctx.output.set_dirty(False)

    @abstractmethod
    def export_file(self, ctx: BakeContext) -> None:
        """Save Bake to disk."""
        LOG.debug("Saving File to Disk ...")
        if ctx.task.output_context.output_settings.path.export_file:
            ImageServiceBake.save(ctx.image)
