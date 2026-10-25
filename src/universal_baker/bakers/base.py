from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Generator
from contextlib import ExitStack, contextmanager
from typing import TYPE_CHECKING, Any

import bpy

from ..constant import ICON_BAKE, LOG
from ..core.property_class_factory import ClassFactory
from ..core.registry_baker import registry_baker
from ..core.registry_definition import registry_definition
from ..enum.image_colorspace import ImageColorSpace
from ..enum.output_stage import OutputStage
from ..parameter.baker_local.metadata_loader import MetadataLoader as metadata_loader_local
from ..parameter.parameter_applier import ParameterApplier
from ..parameter.parameter_context import ParameterContext
from ..runtime.asset_setup import AssetSetup, BakerExecution
from ..runtime.bake_objects import BakeObjects
from ..runtime.color_management_info import ColorManagementInfo
from ..services.artifact_service import ArtifactService
from ..services.bake_material import BakeMaterialService
from ..services.image_bake import ImageServiceBake
from ..services.material import MaterialService
from ..services.renderer import RendererService
from ..services.visibility_override import VisibilityOverride

if TYPE_CHECKING:
    from ..parameter.metadata import ParameterMetadata
    from ..runtime.context_bake import BakeContext
    from ..runtime.task import Task

LOG_SCOPE = "Baking"


def update_baker_property(self, context):
    # TODO: Need to optimize, and make sure only the modified property is updated -> Currently all the properties are
    # updated when one properties is modified
    definition = registry_definition.require(self.name)

    if definition is None:
        return

    for o in bpy.context.scene.objects:
        if o.type != "MESH":
            continue

        materials = [s.material for s in o.material_slots if s is not None and s.material is not None]

        context = ParameterContext(
            object=o,
            materials=materials,
            ui_prop=self,
            is_dragging=bpy.context.scene.ubk_project.visualization.is_dragging,
        )

        ParameterApplier.apply_baker(definition, context)


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
    icon: str = ICON_BAKE
    blender_bake_type = "DIFFUSE"
    accumulator_id = "ALPHA_OVER"
    is_custom: bool = False
    clear_preview_material: bool = True
    viewport_render_pass: str = "COMBINED"
    bake_colorspace: ImageColorSpace = ImageColorSpace.NON_COLOR
    image_colorspace: ImageColorSpace = ImageColorSpace.NON_COLOR
    color_management_info = ColorManagementInfo()

    def poll(self, task: Task) -> bool:
        """Whether this baker can execute this task."""
        return True

    @property
    def parameters(self) -> tuple[ParameterMetadata, ...]:
        parameters: tuple[ParameterMetadata, ...] = ()
        return parameters

    @property
    def property_class_name(self) -> str:
        return f"UBK_{self.name.replace(' ', '')}Properties"

    @property
    def settings_name(self) -> str:
        return f"{self.name.lower().replace(' ', '_')}_settings"

    @abstractmethod
    @contextmanager
    def prepare_execution(
        self,
        bake_objects: BakeObjects,
    ) -> Generator[BakerExecution, Any, Any]:

        material_setup = BakeMaterialService.prepare(
            targets=[bake_objects.target_object],
            sources=bake_objects.source_objects,
        )
        baker_setup = AssetSetup(material_setup=material_setup)

        hide_render = {}

        for s in bake_objects.baker_material_objects:
            hide_render[s] = s.hide_render

        try:
            yield BakerExecution(
                target=bake_objects.target_object,
                cage=bake_objects.cage_object,
                sources=bake_objects.source_objects,
                setup=baker_setup,
            )

        finally:
            for obj, render in hide_render.items():
                obj.hide_render = render

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

            try:
                visibility_overrides = self.get_visibility_overrides(ctx)
                self.invalidate_previous_output(ctx)
                self.prepare(ctx)

                with ExitStack() as stack:
                    for vo in visibility_overrides:
                        stack.enter_context(vo)

                    self.bake(ctx)

                self.update_baker(ctx)
                self.export_file(ctx)
                self.create_artifact(ctx)

            finally:
                self.cleanup(ctx)

    @abstractmethod
    def invalidate_previous_output(self, ctx: BakeContext):
        if not ctx.session.output_invalidated:
            LOG.debug("Invalidate Previous Output ...")
            ctx.session.runtime.outputs.invalidate(
                ctx.task.bake_group_uuid,
                ctx.task.baker_uuid,
            )

            ctx.session.output_invalidated = True

    @abstractmethod
    def prepare(self, ctx: BakeContext) -> None:
        """Prepare Blender before baking."""
        LOG.debug("Preparing Scene ...")

        ctx.image = ImageServiceBake.acquire(ctx.image, ctx.task)

        MaterialService.prepare(ctx)

        self.apply_parameters(ctx)

    @abstractmethod
    def get_visibility_overrides(self, ctx: BakeContext) -> list[VisibilityOverride]:
        """Get Visibility."""
        l: list[VisibilityOverride] = []
        return l

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

        baker = BakeController.get_baker_from_uuid(ctx.task.baker_uuid)

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
            producer_uuid=ctx.task.baker_uuid,
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
            LOG.debug("Output Artifact not found")
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

        materials = ctx.baker_materials

        if materials is None:
            LOG.error("Material Overrides not found")
            return

        objects = ctx.baker_material_objects

        LOG.debug("Applying baker parameters")
        for o in objects:
            object_materials = materials.get(o.name)

            if object_materials is None:
                LOG.error(f"Material Overrides not found for {o.name}")
                continue

            parameter_context = ParameterContext(
                object=o,
                materials=object_materials.materials,
                scene=ctx.scene,
                ui_prop=getattr(ctx.task.baker_settings, self.settings_name),
            )

            ParameterApplier.apply_baker(
                definition,
                parameter_context,
            )

    def register_local(self):
        LOG.info(f"Registering Building Baker : {self.id}")
        self.register_property_class()
        registry_baker.register(self)

        registry_definition.register_local_lazy(
            identifier=self.id,
            definition_object=self,
            loader=metadata_loader_local.load_definition,
        )

    def register_property_class(self):
        c = ClassFactory(self.property_class_name, None, bpy.types.PropertyGroup)
        c.__annotations__["name"] = bpy.props.StringProperty(name="Baker ID", default=self.id)

        for p in self.parameters:
            LOG.info(f"Registering {self.id} Property : {p.identifier}")
            c.__annotations__[p.identifier] = p.blender_property(update_baker_property)

        from bpy.utils import register_class

        register_class(c)

        from ..parameters_definition.baker_settings import UBK_BakerSettings

        UBK_BakerSettings.__annotations__[self.settings_name] = bpy.props.PointerProperty(type=c)
