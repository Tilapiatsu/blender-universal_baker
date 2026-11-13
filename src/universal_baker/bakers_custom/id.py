from __future__ import annotations

from ..core.registry_baker import registry_baker
from ..enum.image_colorspace import ImageColorSpace
from ..enum.view_transform import DisplayDevice, ViewTransform
from ..parameter.metadata import BindingMetadata, BindingType, ParameterMetadata
from ..parameter.parameter import ParameterSource, ParameterType
from ..runtime.color_management_info import ColorManagementInfo
from .base import CustomBaker


class ID(CustomBaker):
    id = "ID"
    name = "ID"
    description = "ID baker."
    icon = "TEXTURE"
    blender_bake_type = "EMIT"
    accumulator_id = "ALPHA_OVER"
    clear_preview_material: bool = True
    bake_colorspace: ImageColorSpace = ImageColorSpace.NON_COLOR
    image_colorspace: ImageColorSpace = ImageColorSpace.SRGB
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
                modifier="GN_ID",
                property="properties.inputs.Socket_3.value",
            ),
        )
        p = ParameterMetadata(
            identifier="Material",
            name="Material",
            source=ParameterSource.UI,
            default=True,
            description="Material ID.",
            type=ParameterType.BOOL,
            category="ID",
            order=0,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MODIFIER_PROPERTY,
                modifier="GN_ID",
                property="properties.inputs.Socket_7.value",
            ),
        )
        p = ParameterMetadata(
            identifier="MeshIsland",
            name="Mesh Island",
            source=ParameterSource.UI,
            default=False,
            description="Material ID.",
            type=ParameterType.BOOL,
            category="ID",
            order=1,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MODIFIER_PROPERTY,
                modifier="GN_ID",
                property="properties.inputs.Socket_8.value",
            ),
        )
        p = ParameterMetadata(
            identifier="Object",
            name="Object",
            source=ParameterSource.UI,
            default=False,
            description="Object ID.",
            type=ParameterType.BOOL,
            category="ID",
            order=2,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MODIFIER_PROPERTY,
                modifier="GN_ID",
                property="properties.inputs.Socket_6.value",
            ),
        )
        p = ParameterMetadata(
            identifier="UDIM",
            name="UDIM",
            source=ParameterSource.UI,
            default=False,
            description="UDIM ID.",
            type=ParameterType.BOOL,
            category="ID",
            order=3,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MODIFIER_PROPERTY,
                modifier="GN_ID",
                property="properties.inputs.Socket_4.value",
            ),
        )
        p = ParameterMetadata(
            identifier="UVIsland",
            name="UV Island",
            source=ParameterSource.UI,
            default=False,
            description="UV Island ID.",
            type=ParameterType.BOOL,
            category="ID",
            order=4,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MODIFIER_PROPERTY,
                modifier="GN_ID",
                property="properties.inputs.Socket_5.value",
            ),
        )
        p = ParameterMetadata(
            identifier="UVMap",
            name="UVMap Name",
            source=ParameterSource.UI,
            default="UVMap",
            description="UVMap Name.",
            type=ParameterType.STRING,
            category="ID",
            order=5,
            visible=False,
            bindings=b,
        )

        parameters += (p,)

        return parameters


classes = (ID,)


def register():
    for c in classes:
        baker = c()
        baker.register_custom()


def unregister():
    for c in classes:
        registry_baker.unregister_custom(c.id)


def refresh():
    unregister()
    register()
