from __future__ import annotations

from ..core.registry_baker import registry_baker
from ..enum.image_colorspace import ImageColorSpace
from ..enum.view_transform import DisplayDevice, ViewTransform
from ..parameter.metadata import BindingMetadata, BindingType, ParameterMetadata
from ..parameter.parameter import ParameterSource, ParameterType
from ..runtime.color_management_info import ColorManagementInfo
from .base import CustomBaker


class Thickness(CustomBaker):
    id = "THICKNESS"
    name = "Thickness"
    description = "Thickness baker."
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
                binding_type=BindingType.MATERIAL_SOCKET,
                material="UBK_Thickness",
                node="Ambient Occlusion",
                socket_input="Distance",
            ),
        )
        p = ParameterMetadata(
            identifier="Distance",
            name="Distance",
            source=ParameterSource.UI,
            default=1.0,
            description="Thickness Distance.",
            type=ParameterType.FLOAT,
            soft_min=0.0,
            soft_max=1000000.0,
            min_value=0.0,
            max_value=1000000.0,
            category="Thickness",
            order=0,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MATERIAL_SOCKET,
                material="UBK_Thickness",
                node="Ambient Occlusion",
                socket_input="only_local",
            ),
        )
        p = ParameterMetadata(
            identifier="OnlyLocal",
            name="Only Local",
            source=ParameterSource.UI,
            default=False,
            description="Compute Thickness without considering neighboors objects.",
            type=ParameterType.BOOL,
            category="Thickness",
            order=1,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MATERIAL_SOCKET,
                material="UBK_Thickness",
                node="SN_Bake_CC",
                socket_input="GlobalContrast",
            ),
        )
        p = ParameterMetadata(
            identifier="GlobalContrast",
            name="Global Contrast",
            source=ParameterSource.UI,
            default=1.0,
            description="Thickness Global Contrast.",
            type=ParameterType.FLOAT,
            soft_min=0.0,
            soft_max=1.0,
            min_value=0.0,
            max_value=1.0,
            category="Thickness",
            order=2,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MATERIAL_SOCKET,
                material="UBK_Thickness",
                node="SN_Bake_CC",
                socket_input="FineContrast",
            ),
        )
        p = ParameterMetadata(
            identifier="FineContrast",
            name="Fine Contrast",
            source=ParameterSource.UI,
            default=0.0,
            description="Thickness Fine Contrast.",
            type=ParameterType.FLOAT,
            soft_min=0.0,
            soft_max=0.999,
            min_value=0.0,
            max_value=0.999,
            category="Thickness",
            order=3,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MATERIAL_SOCKET,
                material="UBK_Thickness",
                node="SN_Bake_CC",
                socket_input="Gamma",
            ),
        )
        p = ParameterMetadata(
            identifier="Gamma",
            name="Gamma",
            source=ParameterSource.UI,
            default=1.0,
            description="Thickness Gamma.",
            type=ParameterType.FLOAT,
            soft_min=0.001,
            soft_max=10.0,
            min_value=0.001,
            max_value=10.0,
            category="Thickness",
            order=4,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        return parameters


classes = (Thickness,)


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
