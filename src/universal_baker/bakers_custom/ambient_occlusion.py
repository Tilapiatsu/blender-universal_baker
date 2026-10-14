from __future__ import annotations

from ..core.registry_baker import registry_baker
from ..enum.image_colorspace import ImageColorSpace
from ..enum.view_transform import DisplayDevice, ViewTransform
from ..parameter.metadata import BindingMetadata, BindingType, ParameterMetadata
from ..parameter.parameter import ParameterType
from ..runtime.color_management_info import ColorManagementInfo
from .base import CustomBaker


class AmbientOcclusion(CustomBaker):
    id = "AMBIENT_OCCLUSION"
    name = "Ambient Occlusion"
    description = "Ambient Occlusion baker."
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
                material="UBK_Ambient_Occlusion",
                node="Ambient Occlusion",
                socket_input="Distance",
            ),
        )
        p = ParameterMetadata(
            identifier="Distance",
            name="Distance",
            default=0.0,
            description="Ambient Occlusion Distance.",
            type=ParameterType.FLOAT,
            soft_min=0.0,
            soft_max=1000000.0,
            min_value=0.0,
            max_value=1000000.0,
            category="Ambient Occlusion",
            order=0,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MATERIAL_SOCKET,
                material="UBK_Ambient_Occlusion",
                node="Ambient Occlusion",
                socket_input="only_local",
            ),
        )
        p = ParameterMetadata(
            identifier="OnlyLocal",
            name="Only Local",
            default=False,
            description="Compute Ambient Occlusion without considering neighboors objects.",
            type=ParameterType.BOOL,
            category="Ambient Occlusion",
            order=1,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MATERIAL_SOCKET,
                material="UBK_Ambient_Occlusion",
                node="SN_Bake_CC",
                socket_input="GlobalContrast",
            ),
        )
        p = ParameterMetadata(
            identifier="GlobalContrast",
            name="Global Contrast",
            default=1.0,
            description="Ambient Occlusion Global Contrast.",
            type=ParameterType.FLOAT,
            soft_min=-5.0,
            soft_max=5.0,
            min_value=-5.0,
            max_value=5.0,
            category="Ambient Occlusion",
            order=2,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MATERIAL_SOCKET,
                material="UBK_Ambient_Occlusion",
                node="SN_Bake_CC",
                socket_input="FineContrast",
            ),
        )
        p = ParameterMetadata(
            identifier="FineContrast",
            name="Fine Contrast",
            default=0.0,
            description="Ambient Occlusion Fine Contrast.",
            type=ParameterType.FLOAT,
            soft_min=0.0,
            soft_max=0.999,
            min_value=0.0,
            max_value=0.999,
            category="Ambient Occlusion",
            order=3,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MATERIAL_SOCKET,
                material="UBK_Ambient_Occlusion",
                node="SN_Bake_CC",
                socket_input="Gamma",
            ),
        )
        p = ParameterMetadata(
            identifier="Gamma",
            name="Gamma",
            default=1.0,
            description="Ambient Occlusion Gamma.",
            type=ParameterType.FLOAT,
            soft_min=0.001,
            soft_max=10.0,
            min_value=0.001,
            max_value=10.0,
            category="Ambient Occlusion",
            order=4,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        return parameters


classes = (AmbientOcclusion,)


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
