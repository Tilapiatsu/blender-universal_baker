from __future__ import annotations

from ..core.registry_baker import registry_baker
from ..enum.image_colorspace import ImageColorSpace
from ..enum.view_transform import DisplayDevice, ViewTransform
from ..parameter.metadata import BindingMetadata, BindingType, ParameterMetadata
from ..parameter.parameter import ParameterSource, ParameterType
from ..runtime.color_management_info import ColorManagementInfo
from .base import BakerBase


class Diffuse(BakerBase):
    """Bake the diffuse color."""

    id = "DIFFUSE"
    name = "Diffuse"
    description = "Bake diffuse color"
    icon = "TEXTURE"
    blender_bake_type = "DIFFUSE"
    accumulator_id = "ALPHA_OVER"
    clear_preview_material: bool = False
    bake_colorspace: ImageColorSpace = ImageColorSpace.ACES_2_0
    image_colorspace: ImageColorSpace = ImageColorSpace.SRGB
    color_management_info = ColorManagementInfo(
        apply_view_transform=True,
        display_device=DisplayDevice.SRGB,
        view_transform=ViewTransform.ACES_2_0,
        look="None",
        exposure=0.0,
        gamma=1.0,
    )

    @property
    def parameters(self) -> tuple[ParameterMetadata, ...]:
        parameters: tuple[ParameterMetadata, ...] = ()

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.SCENE_PROPERTY,
                property="render.bake.use_pass_direct",
            ),
        )
        p = ParameterMetadata(
            identifier="contribution_direct",
            name="Direct",
            source=ParameterSource.UI,
            default=True,
            description="Add Direct Lighting Contribution",
            type=ParameterType.BOOL,
            category="Contribution",
            order=0,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.SCENE_PROPERTY,
                property="render.bake.use_pass_indirect",
            ),
        )
        p = ParameterMetadata(
            identifier="contribution_indirect",
            name="Indirect",
            source=ParameterSource.UI,
            default=True,
            description="Add Indirect Lighting Contribution",
            type=ParameterType.BOOL,
            category="Contribution",
            order=1,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.SCENE_PROPERTY,
                property="render.bake.use_pass_color",
            ),
        )
        p = ParameterMetadata(
            identifier="contribution_color",
            name="Color",
            source=ParameterSource.UI,
            default=True,
            description="Color the pass",
            type=ParameterType.BOOL,
            category="Contribution",
            order=2,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        return parameters


classes = (Diffuse,)


def register():
    for c in classes:
        baker = c()
        baker.register_local()


def unregister():
    for c in classes:
        registry_baker.unregister(c.id)
