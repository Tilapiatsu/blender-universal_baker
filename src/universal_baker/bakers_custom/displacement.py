from __future__ import annotations

from typing import Any

from ..core.registry_baker import registry_baker
from ..enum.image_colorspace import ImageColorSpace
from ..enum.view_transform import DisplayDevice, ViewTransform
from ..parameter.metadata import BindingMetadata, BindingType, ParameterMetadata
from ..parameter.parameter import ParameterOption, ParameterSource, ParameterType
from ..parameter.parameter_context import ParameterContext
from ..runtime.color_management_info import ColorManagementInfo
from .base import CustomBaker


class Displacement(CustomBaker):
    id = "DISPLACEMENT"
    name = "Displacement"
    description = "Displacement baker."
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
                modifier="UBK_Displacement",
                property="property.inputs.Socket_2.value",
            ),
        )
        p = ParameterMetadata(
            identifier="Object",
            name="Object",
            source=ParameterSource.FUNCTION,
            default="NONE",
            description="The Target Object.",
            type=ParameterType.OBJ,
            category="Displacement",
            order=0,
            visible=False,
            bindings=b,
        )

        parameters += (p,)

        options = (
            ParameterOption(
                identifier="DISPLACEMENT",
                label="Displacement",
            ),
            ParameterOption(
                identifier="VECTOR_DISPLACEMENT",
                label="Vector Displacement",
            ),
        )

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MODIFIER_PROPERTY,
                modifier="UBK_Displacement",
                property="property.inputs.Socket_3.value",
            ),
        )
        p = ParameterMetadata(
            identifier="Mode",
            name="Mode",
            source=ParameterSource.UI,
            default="DISPLACEMENT",
            description="Choose beetween Vector Displamenet and regular Displacement.",
            type=ParameterType.ENUM,
            options=options,
            category="Displacement",
            order=1,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        options = (
            ParameterOption(
                identifier="MANUAL",
                label="Manual",
            ),
            ParameterOption(
                identifier="ABSOLUTE",
                label="Absolute",
            ),
        )

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MODIFIER_PROPERTY,
                modifier="UBK_Displacement",
                property="property.inputs.Socket_4.value",
            ),
        )
        p = ParameterMetadata(
            identifier="Normalization",
            name="Normalization",
            source=ParameterSource.UI,
            default="MANUAL",
            description="How to Normalize displacement Value.",
            type=ParameterType.ENUM,
            category="Displacement",
            options=options,
            order=2,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MODIFIER_PROPERTY,
                modifier="UBK_Displacement",
                property="property.inputs.Socket_7.value",
            ),
        )
        p = ParameterMetadata(
            identifier="DebugClipping",
            name="Debug Clipping",
            source=ParameterSource.UI,
            default=False,
            description="Display Clipping Values.",
            type=ParameterType.BOOL,
            category="Displacement",
            options=options,
            order=2,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MODIFIER_PROPERTY,
                modifier="UBK_Displacement",
                property="property.inputs.Socket_5.value",
            ),
        )
        p = ParameterMetadata(
            identifier="Min",
            name="Min",
            source=ParameterSource.UI,
            default=-0.5,
            min_value=-100000.0,
            max_value=100000.0,
            soft_min=-1000000.0,
            soft_max=1000000.0,
            description="How to Normalize displacement Value.",
            type=ParameterType.FLOAT,
            category="Displacement",
            order=3,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.MODIFIER_PROPERTY,
                modifier="UBK_Displacement",
                property="property.inputs.Socket_6.value",
            ),
        )
        p = ParameterMetadata(
            identifier="Max",
            name="Max",
            source=ParameterSource.UI,
            default=0.5,
            min_value=-100000.0,
            max_value=100000.0,
            soft_min=-1000000.0,
            soft_max=1000000.0,
            description="How to Normalize displacement Value.",
            type=ParameterType.FLOAT,
            category="Displacement",
            order=4,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        return parameters

    def parameter_value(self, value_name: str, context: ParameterContext) -> Any:
        if context.bake_targets is None:
            return None

        target = None
        for o in context.bake_targets:
            if o.uuid == context.target_uuid:
                target = o.target
                break

        if target is None:
            return None

        match value_name:
            case "Object":
                return target
            case _:
                return None


classes = (Displacement,)


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
