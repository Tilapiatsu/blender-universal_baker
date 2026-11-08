from __future__ import annotations

import bpy

from ..core.registry_baker import registry_baker
from ..enum.image_colorspace import ImageColorSpace
from ..enum.view_transform import DisplayDevice, ViewTransform
from ..parameter.metadata import BindingMetadata, BindingType, ParameterMetadata
from ..parameter.parameter import ParameterOption, ParameterType
from ..runtime.color_management_info import ColorManagementInfo
from ..runtime.context_bake import BakeContext
from .base import CustomBaker


class Position(CustomBaker):
    id = "POSITION"
    name = "Position"
    description = "Position baker."
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
                modifier="GN_StoreBBoxVectors",
                property="properties.inputs.Socket_3.value",
            ),
        )
        options = (
            ParameterOption(
                identifier="ABSOLUTE",
                label="Absolute",
            ),
            ParameterOption(
                identifier="BAKE_GROUP",
                label="Bake Group",
            ),
            ParameterOption(
                identifier="TARGET",
                label="Target",
            ),
        )
        p = ParameterMetadata(
            identifier="Normalization",
            name="Normalization",
            default="BAKE_GROUP",
            options=options,
            description="How to normalize the position values.",
            type=ParameterType.ENUM,
            category="Position",
            order=0,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MODIFIER_PROPERTY,
                modifier="GN_StoreBBoxVectors",
                property="properties.inputs.Socket_4.value",
            ),
        )
        p = ParameterMetadata(
            identifier="Collection",
            name="Collection",
            default="BAKE_GROUP",
            description="The Collection containing all the objects from the same bake group.",
            type=ParameterType.COLLECTION,
            category="Position",
            order=1,
            visible=False,
            bindings=b,
        )

        parameters += (p,)

        return parameters

    def prepare_custom_collection(self, ctx: BakeContext) -> bpy.types.Collection | None:
        return super().prepare_custom_collection(ctx)


classes = (Position,)


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
