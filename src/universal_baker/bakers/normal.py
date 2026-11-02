from __future__ import annotations

import bpy

from ..core.registry_baker import registry_baker
from ..enum.image_colorspace import ImageColorSpace
from ..enum.view_transform import DisplayDevice, ViewTransform
from ..parameter.metadata import BindingMetadata, BindingType, ParameterMetadata
from ..parameter.parameter import ParameterOption, ParameterType
from ..runtime.bake_objects import BakeObjects
from ..runtime.color_management_info import ColorManagementInfo
from ..runtime.context_bake import BakeContext
from ..services.visibility_override import VisibilityOverride
from .base import BakerBase


class NormalBaker(BakerBase):
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

    def execute(self, ctx: BakeContext) -> None:
        return super().execute(ctx)

    def invalidate_previous_output(self, ctx: BakeContext) -> None:
        super().invalidate_previous_output(ctx)

    def prepare_execution(
        self,
        bake_objects: BakeObjects,
    ):
        return super().prepare_execution(bake_objects)

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

    def get_visibility_overrides(self, ctx: BakeContext) -> list[VisibilityOverride]:
        """Set Visibility."""
        l: list[VisibilityOverride] = []
        return l

    def prepare(self, ctx: BakeContext):
        """
        Prepare everything required before Blender's bake.
        """
        super().prepare(ctx)

    def bake(self, ctx: BakeContext) -> None:
        """Execute the bake."""
        return super().bake(ctx)

    def cleanup(self, ctx: BakeContext):
        """
        Cleanup after baking.
        """
        super().cleanup(ctx)

    def update_baker(self, ctx: BakeContext) -> None:
        return super().update_baker(ctx)

    def create_artifact(self, ctx: BakeContext) -> None:
        return super().create_artifact(ctx)

    def export_file(self, ctx: BakeContext):
        """Save Bake to disk."""
        super().export_file(ctx)


classes = (NormalBaker,)


def register():
    for c in classes:
        baker = c()
        baker.register_local()


def unregister():
    for c in classes:
        registry_baker.unregister(c.id)
