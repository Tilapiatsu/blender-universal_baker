from __future__ import annotations

from ..core.registry_baker import registry_baker
from ..enum.image_colorspace import ImageColorSpace
from ..enum.view_transform import DisplayDevice, ViewTransform
from ..parameter.metadata import BindingMetadata, BindingType, ParameterMetadata
from ..parameter.parameter import ParameterOption, ParameterSource, ParameterType
from ..runtime.color_management_info import ColorManagementInfo
from .base import BakerBase


class Normal(BakerBase):
    """Bake the Normal."""

    id = "NORMAL"
    name = "Normal"
    description = "Bake Normal"
    icon = "TEXTURE"
    blender_bake_type = "NORMAL"
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
                binding_type=BindingType.SCENE_PROPERTY,
                property="render.bake.normal_space",
            ),
        )
        options = (
            ParameterOption(
                identifier="TANGENT",
                label="Tangent",
            ),
            ParameterOption(
                identifier="OBJECT",
                label="Object",
            ),
        )
        p = ParameterMetadata(
            identifier="normal_space",
            name="Space",
            source=ParameterSource.UI,
            default="TANGENT",
            description="Choose Normal Space for Baking.",
            type=ParameterType.ENUM,
            options=options,
            category="Influence",
            order=0,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        options = (
            ParameterOption(
                identifier="POS_X",
                label="+X",
            ),
            ParameterOption(
                identifier="POS_Y",
                label="+Y",
            ),
            ParameterOption(
                identifier="POS_Z",
                label="+Z",
            ),
            ParameterOption(
                identifier="NEG_X",
                label="-X",
            ),
            ParameterOption(
                identifier="NEG_Y",
                label="-Y",
            ),
            ParameterOption(
                identifier="NEG_Z",
                label="-Z",
            ),
        )

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.SCENE_PROPERTY,
                property="render.bake.normal_r",
            ),
        )
        p = ParameterMetadata(
            identifier="normal_r",
            source=ParameterSource.UI,
            name="R",
            default="POS_X",
            description="Axis to Bake in Red Channel.",
            type=ParameterType.ENUM,
            options=options,
            category="Influence",
            order=1,
            visible=True,
            bindings=b,
        )
        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.SCENE_PROPERTY,
                property="render.bake.normal_g",
            ),
        )
        p = ParameterMetadata(
            identifier="normal_g",
            name="G",
            source=ParameterSource.UI,
            default="POS_Y",
            description="Axis to Bake in Green Channel.",
            type=ParameterType.ENUM,
            options=options,
            category="Influence",
            order=2,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type=BindingType.SCENE_PROPERTY,
                property="render.bake.normal_b",
            ),
        )
        p = ParameterMetadata(
            identifier="normal_b",
            name="B",
            source=ParameterSource.UI,
            default="POS_Z",
            description="Axis to Bake in Blue Channel.",
            type=ParameterType.ENUM,
            options=options,
            category="Influence",
            order=3,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        return parameters

    def configure_preview_material(self, material):
        # TODO: Need to bind the same bake settings :
        # Space: Tangent / Object
        # R
        # G
        # B
        material.use_nodes = True
        nodes = material.node_tree.nodes
        nodes.clear()

        output = nodes.new("ShaderNodeOutputMaterial")
        normal = nodes.new("ShaderNodeNewGeometry")
        add = nodes.new("ShaderNodeVectorMath")
        multiply = nodes.new("ShaderNodeVectorMath")
        value = nodes.new("ShaderNodeValue")

        add.operation = "ADD"
        multiply.operation = "MULTIPLY"
        add.inputs[1].default_value[0] = 1.0
        add.inputs[1].default_value[1] = 1.0
        add.inputs[1].default_value[2] = 1.0
        value.outputs[0].default_value = 0.5

        material.node_tree.links.new(
            normal.outputs["Normal"],
            add.inputs[0],
        )

        material.node_tree.links.new(
            add.outputs["Vector"],
            multiply.inputs[0],
        )

        material.node_tree.links.new(
            value.outputs[0],
            multiply.inputs[1],
        )

        material.node_tree.links.new(
            multiply.outputs["Vector"],
            output.inputs["Surface"],
        )

        multiply.location.x = output.location.x - 200
        add.location.x = multiply.location.x - 200
        normal.location.x = add.location.x - 200
        value.location.x = add.location.x
        value.location.y = add.location.y - 200


classes = (Normal,)


def register():
    for c in classes:
        baker = c()
        baker.register_local()


def unregister():
    for c in classes:
        registry_baker.unregister(c.id)
