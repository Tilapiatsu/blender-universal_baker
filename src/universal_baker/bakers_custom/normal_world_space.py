from __future__ import annotations

import bpy

from ..core.registry_baker import registry_baker
from ..enum.image_colorspace import ImageColorSpace
from ..enum.view_transform import DisplayDevice, ViewTransform
from ..parameter.metadata import BindingMetadata, BindingType, ParameterMetadata
from ..parameter.parameter import ParameterType
from ..runtime.color_management_info import ColorManagementInfo
from ..runtime.context_bake import BakeContext
from .base import CustomBaker


class NormalWorldSpace(CustomBaker):
    id = "NORMAL_WORLD_SPACE"
    name = "Normal World Space"
    description = "Normal World Space baker."
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
                material="UBK_Normal_WS",
                node="SN_InvertChannel",
                socket_input="Invert X",
            ),
        )
        p = ParameterMetadata(
            identifier="invert_x",
            name="Invert X",
            default=False,
            description="Invert X Channel.",
            type=ParameterType.BOOL,
            category="NormalWS",
            order=0,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MATERIAL_SOCKET,
                material="UBK_Normal_WS",
                node="SN_InvertChannel",
                socket_input="Invert Y",
            ),
        )

        p = ParameterMetadata(
            identifier="invert_y",
            name="Invert Y",
            default=False,
            description="Invert Y Channel.",
            type=ParameterType.BOOL,
            category="NormalWS",
            order=1,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MATERIAL_SOCKET,
                material="UBK_Normal_WS",
                node="SN_InvertChannel",
                socket_input="Invert Z",
            ),
        )

        p = ParameterMetadata(
            identifier="invert_z",
            name="Invert Z",
            default=False,
            description="Invert Z Channel.",
            type=ParameterType.BOOL,
            category="NormalWS",
            order=2,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        return parameters


classes = (NormalWorldSpace,)


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
