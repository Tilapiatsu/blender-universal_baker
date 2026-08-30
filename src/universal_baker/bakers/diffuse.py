from __future__ import annotations

import bpy

from .base import BakerBase

from ..runtime.context_bake import BakeContext
from ..enum.image_colorspace import ImageColorSpace
from ..core.registry_baker import registry_baker

from ..parameter.metadata import ParameterMetadata
from ..parameter.metadata import BindingMetadata


class DiffuseBaker(BakerBase):
    """Bake the diffuse/albedo color."""

    id = "DIFFUSE"
    name = "Diffuse"
    description = "Bake diffuse color"
    icon = "TEXTURE"
    blender_bake_type = "DIFFUSE"
    accumulator_id = "ALPHA_OVER"
    colorspace: ImageColorSpace = ImageColorSpace.SRGB
    clear_preview_material: bool = False

    @property
    def parameters(self) -> tuple[ParameterMetadata, ...]:
        parameters: tuple[ParameterMetadata, ...] = ()

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type="SCENE_PROPERTY",
                scene=bpy.context.scene.name,
                property=".render.bake.use_pass_direct",
            ),
        )
        p = ParameterMetadata(
            identifier="contribution_direct",
            name="Direct",
            default=True,
            description="Add Direct Lighting Contribution",
            type="BOOL",
            category="Contribution",
            order=0,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type="SCENE_PROPERTY",
                scene=bpy.context.scene.name,
                property=".render.bake.use_pass_indirect",
            ),
        )
        p = ParameterMetadata(
            identifier="contribution_indirect",
            name="Indirect",
            default=True,
            description="Add Indirect Lighting Contribution",
            type="BOOL",
            category="Contribution",
            order=1,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type="SCENE_PROPERTY",
                scene=bpy.context.scene.name,
                property=".render.bake.use_pass_color",
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
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        return parameters

    def execute(self, ctx: BakeContext) -> None:
        return super().execute(ctx)

    def prepare_execution(self, target):
        return super().prepare_execution(target)

    def configure_preview_material(self, material): ...

    def prepare(self, ctx: BakeContext):
        """
        Prepare everything required before Blender's bake.
        """
        super().prepare(ctx)

    def bake(self, ctx: BakeContext) -> None:
        """Execute the bake."""
        return super().bake(ctx)

    def cleanup(self, ctx: BakeContext):
        """
        Cleanup after baking.
        """
        super().cleanup(ctx)

    def update_baker(self, ctx: BakeContext) -> None:
        return super().update_baker(ctx)

    def create_artifact(self, ctx: BakeContext) -> None:
        return super().create_artifact(ctx)

    def export_file(self, ctx: BakeContext):
        """Save Bake to disk."""
        super().export_file(ctx)


classes = (DiffuseBaker,)


def register():
    for c in classes:
        registry_baker.register(c())


def unregister():
    for c in classes:
        registry_baker.unregister(c.id)
