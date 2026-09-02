from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any

import bpy

from ..constant import LOG, get_prefs
from ..core.registry_baker import registry_baker
from ..core.registry_definition import registry_definition
from ..enum.bake_colorspace import BakerColorType
from ..enum.image_colorspace import ImageColorSpace
from ..enum.output_stage import OutputStage
from ..enum.view_transform import ViewTransform
from ..parameter.baker_custom.metadata_loader import MetadataLoader as metadata_loader_custom
from ..parameter.baker_local.metadata_loader import MetadataLoader as metadata_loader_local
from ..parameter.parameter_applier import ParameterApplier
from ..parameter.parameter_context import ParameterContext
from ..resources.scene_view_transform import SceneViewTransform
from ..runtime.baker_setup import BakerExecution, BakerSetup
from ..runtime.color_management_info import ColorManagementInfo
from ..services.artifact_service import ArtifactService
from ..services.bake_material import BakeMaterialService
from ..services.image_bake import ImageServiceBake
from ..services.material import MaterialService
from ..services.parameter_service import ParameterService
from ..services.renderer import RendererService

if TYPE_CHECKING:
    from ..parameter.metadata import ParameterMetadata
    from ..runtime.context_bake import BakeContext
    from ..runtime.task import Task

LOG_SCOPE = "Baking"


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
    blender_bake_type = "DIFFUSE"
    accumulator_id = "ALPHA_OVER"
    is_custom: bool = False
    clear_preview_material: bool = True
    asset_path: Path = Path()
    viewport_render_pass: str = "COMBINED"

    # TODO: Need to use color_type and colorspace for baking and displaying baked images
    # Need to expose view transform to bake to -> Diffuse need to use AGX or Aces for nicer result, whereas curvature,
    # occlusion should maybe use Raw because it is just data, and shouldn't be transformed

    bake_colorspace: ImageColorSpace = ImageColorSpace.NON_COLOR
    image_colorspace: ImageColorSpace = ImageColorSpace.NON_COLOR
    view_transform = SceneViewTransform(view_transform=ViewTransform.RAW)
    color_management_info = ColorManagementInfo()

    def poll(self, task: Task) -> bool:
        """Whether this baker can execute this task."""
        return True

    @property
    def parameters(self) -> tuple[ParameterMetadata, ...]:
        parameters: tuple[ParameterMetadata, ...] = ()
        return parameters

    @abstractmethod
    @contextmanager
    def prepare_execution(self, target: bpy.types.Object) -> Generator[BakerExecution, Any, Any]:

        material_setup = BakeMaterialService.prepare(objects=[target])
        baker_setup = BakerSetup(material_setup=material_setup)

        hide_render = target.hide_render
        target.hide_render = False
        try:
            yield BakerExecution(
                target=target,
                setup=baker_setup,
            )

        finally:
            target.hide_render = hide_render
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
            LOG.info(f"{ctx.task!s}")

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

        self.apply_parameters(ctx)

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
            color_management_info=ctx.task.color_management_info,
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
        ImageServiceBake.save(ctx.image, ctx.task.color_management_info)

    def apply_parameters(self, ctx: BakeContext):
        definition = registry_definition.get(self.id)
        if definition is None:
            LOG.error("Parameter definition not found")
            return

        state = ctx.task.baker_settings
        if state is None:
            LOG.error("Bake Settings not found")
            return

        snapshot = ParameterService.snapshot(definition, state)

        LOG.debug("Applying baker parameters")

        materials = ctx.materials.materials

        if materials is None:
            LOG.error(f"Material Overries not found for {ctx.target.name}")
            return

        parameter_context = ParameterContext(
            object=ctx.target,
            materials=materials,
            scene=ctx.scene,
        )

        ParameterApplier.apply(
            definition,
            snapshot,
            parameter_context,
        )

    def register_local(self):
        LOG.info(f"Registering Building Baker : {self.id}")
        registry_baker.register(self)

        registry_definition.register_local_lazy(
            identifier=self.id,
            baker=self,
            loader=metadata_loader_local.load_definition,
        )

    @classmethod
    def register_custom(cls):
        prefs = get_prefs()

        for library in prefs.baker_libraries:
            library_root = Path(library.path)
            if not library_root.exists() or not library_root.is_dir():
                LOG.warning(f"Library path is not valid : {library_root}")
                continue

            blend_files = [f for f in library_root.iterdir() if f.is_file() and f.suffix.lower() == ".blend"]

            if len(blend_files) == 0:
                LOG.warning(f"No blend file found in {library.name} library")

            LOG.info(f"Registering Library : {library.name}")
            for blend_file in blend_files:
                custom_baker = cls()
                baker_name = blend_file.stem.upper().replace(" ", "_")
                custom_baker.id += f"_{baker_name}"
                custom_baker.asset_path = blend_file
                custom_baker.name = blend_file.stem.capitalize()
                LOG.info(f"Registering Custom Baker : {baker_name}")
                registry_baker.register(custom_baker)

                registry_definition.register_custom_lazy(
                    identifier=custom_baker.id,
                    asset_path=blend_file,
                    loader=metadata_loader_custom.load_definition,
                )
