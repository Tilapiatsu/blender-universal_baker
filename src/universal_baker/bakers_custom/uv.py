from __future__ import annotations

from typing import Any

from ..core.registry_baker import registry_baker
from ..enum.image_colorspace import ImageColorSpace
from ..enum.view_transform import DisplayDevice, ViewTransform
from ..parameter.metadata import BindingMetadata, BindingType, ParameterMetadata
from ..parameter.parameter import ParameterSource, ParameterType
from ..parameter.parameter_context import ParameterContext
from ..runtime.color_management_info import ColorManagementInfo
from .base import CustomBaker


class UV(CustomBaker):
    id = "UV"
    name = "UV"
    description = "Bake UV"
    icon = "TEXTURE"
    blender_bake_type = "EMIT"
    accumulator_id = "ALPHA_OVER"
    clear_preview_material: bool = True
    bake_colorspace: ImageColorSpace = ImageColorSpace.NON_COLOR
    image_colorspace: ImageColorSpace = ImageColorSpace.NON_COLOR
    color_management_info = ColorManagementInfo(
        apply_view_transform=True,
        display_device=DisplayDevice.SRGB,
        view_transform=ViewTransform.RAW,
        look="None",
        exposure=0.0,
        gamma=1.0,
    )

    @property
    def parameters(self) -> tuple[ParameterMetadata, ...]:
        parameters: tuple[ParameterMetadata, ...] = ()

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MODIFIER_PROPERTY,
                modifier="GN_UV",
                property="properties.inputs.Socket_3.value",
            ),
        )
        p = ParameterMetadata(
            identifier="ActiveUV",
            name="Active UV",
            source=ParameterSource.UI,
            default=True,
            description="Use Active UV.",
            type=ParameterType.BOOL,
            category="UV",
            order=0,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MODIFIER_PROPERTY,
                modifier="GN_UV",
                property="properties.inputs.Socket_5.value",
            ),
        )
        p = ParameterMetadata(
            identifier="ActiveUVMap",
            name="Active UV Map",
            source=ParameterSource.FUNCTION,
            default="UVMap",
            description="Active UVMap Name.",
            type=ParameterType.STRING,
            category="UV",
            order=1,
            visible=False,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MODIFIER_PROPERTY,
                modifier="GN_UV",
                property="properties.inputs.Socket_2.value",
            ),
        )
        p = ParameterMetadata(
            identifier="UVMap",
            name="UVMap Name",
            source=ParameterSource.UI,
            default="UVMap",
            description="UVMap Name.",
            type=ParameterType.STRING,
            category="UV",
            order=2,
            visible=True,
            bindings=b,
        )

        parameters += (p,)
        return parameters

    def parameter_value(self, value_name: str, context: ParameterContext) -> Any:
        if context.bake_targets is None:
            return None

        match value_name:
            case "ActiveUVMap":
                active = getattr(context.ui_prop, "ActiveUV", None)
                if active is None:
                    return None

                if active and context.object.data.uv_layers.active is not None:
                    return context.object.data.uv_layers.active.name

                else:
                    return None
            case _:
                return None


classes = (UV,)


def register():
    for c in classes:
        baker = c()
        baker.register_local()


def unregister():
    for c in classes:
        registry_baker.unregister(c.id)
