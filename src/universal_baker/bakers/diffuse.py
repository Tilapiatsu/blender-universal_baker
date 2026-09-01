from __future__ import annotations

import bpy

from ..core.registry_baker import registry_baker
from ..enum.image_colorspace import ImageColorSpace
from ..enum.view_transform import DisplayDevice, ViewTransform
from ..parameter.metadata import BindingMetadata, ParameterMetadata
from ..resources.scene_view_transform import SceneViewTransform
from ..runtime.color_management_info import ColorManagementInfo
from ..runtime.context_bake import BakeContext
from .base import BakerBase


class DiffuseBaker(BakerBase):
    """Bake the diffuse/albedo color."""

    id = "DIFFUSE"
    name = "Diffuse"
    description = "Bake diffuse color"
    icon = "TEXTURE"
    blender_bake_type = "DIFFUSE"
    accumulator_id = "ALPHA_OVER"
    clear_preview_material: bool = False
    image_colorspace: ImageColorSpace = ImageColorSpace.NON_COLOR
    view_transform = SceneViewTransform(view_transform=ViewTransform.ACES_2_0)
    color_management_info = ColorManagementInfo(
        apply_view_transform=True,
        display_device=DisplayDevice.REC_2020,
        view_transform=ViewTransform.ACES_2_0,
        look="None",
        exposure=1.0,
        gamma=1.0,
    )

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
                property="render.bake.use_pass_indirect",
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
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        return parameters

    def execute(self, ctx: BakeContext) -> None:
        return super().execute(ctx)

    def prepare_execution(self, target):
        return super().prepare_execution(target)

    def configure_preview_material(self, material):
        ...
        # TODO: need to write a preview_material for diffuse

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
        baker = c()
        baker.register_local()


def unregister():
    for c in classes:
        registry_baker.unregister(c.id)
