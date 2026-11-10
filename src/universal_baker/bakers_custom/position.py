from __future__ import annotations

from typing import Any

from ..core.registry_baker import registry_baker
from ..enum.image_colorspace import ImageColorSpace
from ..enum.view_transform import DisplayDevice, ViewTransform
from ..parameter.metadata import BindingMetadata, BindingType, ParameterMetadata
from ..parameter.parameter import ParameterOption, ParameterSource, ParameterType
from ..parameter.parameter_context import ParameterContext
from ..runtime.bounding_box import BoundingBoxService
from ..runtime.color_management_info import ColorManagementInfo
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
            source=ParameterSource.UI,
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
                property="properties.inputs.Socket_5.value",
            ),
        )
        p = ParameterMetadata(
            identifier="BBoxMin",
            name="BBoxMin",
            source=ParameterSource.FUNCTION,
            default=(0.0, 0.0, 0.0),
            description="Bounding Box Minimum Value.",
            type=ParameterType.VECTOR,
            category="Position",
            order=1,
            visible=False,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MODIFIER_PROPERTY,
                modifier="GN_StoreBBoxVectors",
                property="properties.inputs.Socket_6.value",
            ),
        )
        p = ParameterMetadata(
            identifier="BBoxMax",
            name="BBoxMax",
            source=ParameterSource.FUNCTION,
            default=(1.0, 1.0, 1.0),
            description="Bounding Box Maximum Value.",
            type=ParameterType.VECTOR,
            category="Position",
            order=2,
            visible=False,
            bindings=b,
        )

        parameters += (p,)

        return parameters

    def parameter_value(self, value_name: str, context: ParameterContext) -> Any:
        if context.bake_targets is None:
            return None

        match value_name:
            case "BBoxMin":
                min, max = BoundingBoxService.get_world_aabb(context.bake_targets)
                return min
            case "BBoxMax":
                min, max = BoundingBoxService.get_world_aabb(context.bake_targets)
                return max
            case _:
                return None


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
