from __future__ import annotations

from ..core.registry_baker import registry_baker
from ..enum.image_colorspace import ImageColorSpace
from ..parameter.metadata import BindingMetadata, BindingType, ParameterMetadata
from ..parameter.parameter import ParameterSource, ParameterType
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
                binding_type=BindingType.SCENE_PROPERTY,
                property="render.bake.use_pass_direct",
            ),
        )
        p = ParameterMetadata(
            identifier="contribution_direct",
            name="Direct",
            source=ParameterSource.UI,
            default=False,
            description="Add Direct Lighting Contribution",
            type=ParameterType.BOOL,
            category="Contribution",
            order=0,
            visible=False,
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
            default=False,
            description="Add Indirect Lighting Contribution",
            type=ParameterType.BOOL,
            category="Contribution",
            order=1,
            visible=False,
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
            visible=False,
            bindings=b,
        )

        parameters += (p,)

        return parameters


classes = (AlbedoBaker,)


def register():
    for c in classes:
        baker = c()
        baker.register_local()


def unregister():
    for c in classes:
        registry_baker.unregister(c.id)
