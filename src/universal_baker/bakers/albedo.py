from __future__ import annotations

import bpy

from ..core.registry_baker import registry_baker
from ..enum.image_colorspace import ImageColorSpace
from ..parameter.metadata import BindingMetadata, ParameterMetadata
from ..runtime.context_bake import BakeContext
from .base import BakerBase


class AlbedoBaker(BakerBase):
    """Bake the diffuse/albedo color."""

    id = "ALBEDO"
    name = "Albedo"
    description = "Bake Albedo"
    icon = "TEXTURE"
    blender_bake_type = "DIFFUSE"
    accumulator_id = "ALPHA_OVER"
    clear_preview_material: bool = False
    viewport_render_pass: str = "DENOISING_ALBEDO"
    image_colorspace: ImageColorSpace = ImageColorSpace.NON_COLOR

    @property
    def parameters(self) -> tuple[ParameterMetadata, ...]:
        parameters: tuple[ParameterMetadata, ...] = ()

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type="SCENE_PROPERTY",
                scene=bpy.context.scene.name,
                property="render.bake.use_pass_direct",
            ),
        )
        p = ParameterMetadata(
            identifier="contribution_direct",
            name="Direct",
            default=False,
            description="Add Direct Lighting Contribution",
            type="BOOL",
            category="Contribution",
            order=0,
            visible=False,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type="SCENE_PROPERTY",
                scene=bpy.context.scene.name,
                property="render.bake.use_pass_indirect",
            ),
        )
        p = ParameterMetadata(
            identifier="contribution_indirect",
            name="Indirect",
            default=False,
            description="Add Indirect Lighting Contribution",
            type="BOOL",
            category="Contribution",
            order=1,
            visible=False,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type="SCENE_PROPERTY",
                scene=bpy.context.scene.name,
                property="render.bake.use_pass_color",
            ),
        )
        p = ParameterMetadata(
            identifier="contribution_color",
            name="Color",
            default=True,
            description="Color the pass",
            type="BOOL",
            category="Contribution",
            order=2,
            visible=False,
            bindings=b,
        )

        parameters += (p,)

        return parameters

    def execute(self, ctx: BakeContext) -> None:
        return super().execute(ctx)

    def prepare_execution(self, target):
        return super().prepare_execution(target)

    def prepare(self, ctx: BakeContext):
        """
        Prepare everything required before Blender's bake.
        """
        return super().prepare(ctx)

    def configure_preview_material(self, material): ...

    def bake(self, ctx: BakeContext):
        """Execute the bake."""
        return super().bake(ctx)

    def cleanup(self, ctx: BakeContext):
        """
        Cleanup after baking.
        """
        return super().cleanup(ctx)

    def update_baker(self, ctx: BakeContext) -> None:
        return super().update_baker(ctx)

    def create_artifact(self, ctx: BakeContext) -> None:
        return super().create_artifact(ctx)

    def export_file(self, ctx: BakeContext):
        """Save Bake to disk."""
        return super().export_file(ctx)


classes = (AlbedoBaker,)


def register():
    for c in classes:
        baker = c()
        baker.register_local()


def unregister():
    for c in classes:
        registry_baker.unregister(c.id)
