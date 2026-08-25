from __future__ import annotations

import bpy

from ..custom_bakers.definition import CustomBakerDefinition
from ..properties.custom_baker import UBK_CustomBaker
from ..properties.baker_parameter import UBK_BakerParameterValue
from ..services.parameter_service import ParameterService
from ..parameter.parameter import BakerParameterType, BakerParameter


class BakerParameterUI:
    @classmethod
    def draw(cls, layout, definition: CustomBakerDefinition, state: UBK_CustomBaker):

        layout.operator("ubk.refresh_custom_baker_parameters", icon="FILE_REFRESH")
        for parameter in definition.parameters:
            item = ParameterService.find(state, parameter.identifier)

            if item is None:
                continue

            cls._draw_parameter(layout, parameter, item)

    @classmethod
    def _draw_parameter(cls, layout, parameter, item):
        parameter_type = parameter.parameter_type

        if parameter_type is BakerParameterType.FLOAT:
            layout.prop(item, "float_value", text=parameter.name)

        elif parameter_type is BakerParameterType.INT:
            layout.prop(item, "int_value", text=parameter.name)

        elif parameter_type is BakerParameterType.BOOL:
            layout.prop(item, "bool_value", text=parameter.name)

        elif parameter_type is BakerParameterType.ENUM:
            cls._draw_enum(layout, parameter, item)

    @classmethod
    def _draw_enum(cls, layout, parameter: BakerParameter, value: UBK_BakerParameterValue) -> None:
        row = layout.row(align=True)
        row.label(text=parameter.name)

        op = row.operator(
            "ubk.custom_baker_parameter_enum",
            text=cls._enum_label(
                parameter,
                value.string_value,
            ),
        )

        op.parameter_id = parameter.identifier

    @staticmethod
    def _enum_label(parameter: BakerParameter, identifier: str) -> str:

        for option in parameter.options:
            if option.identifier == identifier:
                return option.label

        return identifier


# TODO: To be review
class UBK_OT_CustomBakerParameterEnum(bpy.types.Operator):
    bl_idname = "ubk.custom_baker_parameter_enum"
    bl_label = "Select Parameter"
    bl_description = "Select a custom baker parameter value"

    parameter_id: bpy.props.StringProperty()

    def invoke(
        self,
        context,
        event,
    ):

        # We will populate the menu from the active
        # custom baker definition.

        return context.window_manager.invoke_popup(self)

    def draw(self, context):

        layout = self.layout

        definition = ...
        state = ...

        parameter = definition.get_parameter(self.parameter_id)

        if parameter is None:
            layout.label(text="Unknown parameter", icon="ERROR")
            return

        for option in parameter.options:
            op = layout.operator("ubk.custom_baker_parameter_set_enum", text=option.name)

            op.parameter_id = parameter.identifier
            op.value = option.identifier

    def execute(
        self,
        context,
    ):

        return {"FINISHED"}
