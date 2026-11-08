from __future__ import annotations

from ..core.registry_baker import registry_baker
from ..enum.image_colorspace import ImageColorSpace
from ..enum.view_transform import DisplayDevice, ViewTransform
from ..parameter.metadata import BindingMetadata, BindingType, ParameterMetadata
from ..parameter.parameter import ParameterOption, ParameterType
from ..runtime.color_management_info import ColorManagementInfo
from .base import CustomBaker


class Curvature(CustomBaker):
    id = "CURVATURE"
    name = "Curvature"
    description = "Curvature baker."
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
                material="UBK_Curvature",
                node="Menu Switch",
                socket_input="Menu",
            ),
        )

        options = (
            ParameterOption(
                identifier="SINGLE_CHANNEL",
                label="Single Channel",
            ),
            ParameterOption(
                identifier="SPLITTED_CHANNELS",
                label="Splitted Channels",
            ),
            ParameterOption(
                identifier="CONVEX",
                label="Convex",
            ),
            ParameterOption(
                identifier="CONCAVE",
                label="Concave",
            ),
        )

        p = ParameterMetadata(
            identifier="Mode",
            name="Mode",
            default="SINGLE_CHANNEL",
            description="How to Combine convex and concave areas in channels.",
            type=ParameterType.ENUM,
            category="Curvature",
            options=options,
            order=0,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MATERIAL_SOCKET,
                material="UBK_Curvature",
                node="SN_Curvature",
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
            category="Curvature",
            order=1,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MATERIAL_SOCKET,
                material="UBK_Curvature",
                node="SN_Curvature",
                socket_input="FineContrast",
            ),
        )
        p = ParameterMetadata(
            identifier="FineContrast",
            name="Fine Contrast",
            default=0.9,
            description="Ambient Occlusion Fine Contrast.",
            type=ParameterType.FLOAT,
            soft_min=0.0,
            soft_max=0.999,
            min_value=0.0,
            max_value=0.999,
            category="Curvature",
            order=2,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MATERIAL_SOCKET,
                material="UBK_Curvature",
                node="SN_Curvature",
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
            category="Curvature",
            order=3,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        return parameters


classes = (Curvature,)


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
