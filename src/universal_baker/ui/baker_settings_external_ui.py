from __future__ import annotations

import bpy

from ..core.registry_definition import registry_definition
from ..parameter.baker_custom.definition import CustomBakerDefinition
from ..parameter.baker_local.definition import LocalDefinition
from ..parameter.parameter import Parameter, ParameterType
from ..properties.custom_baker import UBK_CustomBaker
from ..properties.parameter_value import UBK_ParameterValue
from ..services.parameter_service import ParameterService


class BakerParameterUI:
    @classmethod
    def draw(cls, layout, definition: CustomBakerDefinition | LocalDefinition, state: UBK_CustomBaker):

        if isinstance(definition, CustomBakerDefinition):
            layout.operator("ubk.refresh_custom_baker_parameters", icon="FILE_REFRESH")

        for parameter in definition.parameters:
            if not parameter.visible:
                continue

            item = ParameterService.find(state, parameter.identifier)

            if item is None:
                continue

            cls._draw_parameter(layout, parameter, item, definition)

    @classmethod
    def _draw_parameter(cls, layout, parameter, item, definition: CustomBakerDefinition | LocalDefinition):
        parameter_type = parameter.parameter_type

        if parameter_type is ParameterType.FLOAT:
            layout.prop(item, "float_value", text=parameter.name)

        elif parameter_type is ParameterType.INT:
            layout.prop(item, "int_value", text=parameter.name)

        elif parameter_type is ParameterType.BOOL:
            layout.prop(item, "bool_value", text=parameter.name)

        elif parameter_type is ParameterType.ENUM:
            cls._draw_enum(layout, parameter, item, definition)

    @classmethod
    def _draw_enum(
        cls,
        layout,
        parameter: Parameter,
        value: UBK_ParameterValue,
        definition: CustomBakerDefinition | LocalDefinition,
    ) -> None:
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
        op.definition_id = definition.identifier

    @staticmethod
    def _enum_label(parameter: Parameter, identifier: str) -> str:

        for option in parameter.options:
            if option.identifier == identifier:
                return option.label

        return identifier


class UBK_OT_CustomBakerParameterEnum(bpy.types.Operator):
    bl_idname = "ubk.custom_baker_parameter_enum"
    bl_label = "Select Parameter"
    bl_description = "Select a custom baker parameter value"

    parameter_id: bpy.props.StringProperty()
    definition_id: bpy.props.StringProperty()

    def invoke(
        self,
        context,
        event,
    ):

        return context.window_manager.invoke_popup(self)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        self.definition = registry_definition.get(self.definition_id)

        if self.definition is None:
            return

        parameter = self.definition.get_parameter(self.parameter_id)

        if parameter is None:
            layout.label(text="Unknown parameter", icon="ERROR")
            return

        for option in parameter.options:
            op = layout.operator("ubk.custom_baker_parameter_set_enum", text=option.label)

            op.parameter_id = parameter.identifier
            op.value = option.identifier

    def execute(
        self,
        context,
    ):

        return {"FINISHED"}


class UBK_OT_CustomBakerParameterEnumOptions(bpy.types.Operator):
    bl_idname = "ubk.custom_baker_parameter_set_enum"
    bl_label = "Select Parameter"
    bl_description = "Select a custom baker parameter value"

    parameter_id: bpy.props.StringProperty()
    value: bpy.props.StringProperty()

    # def invoke(
    #     self,
    #     context,
    #     event,
    # ):
    #
    #     return context.window_manager.invoke_popup(self)
    #
    # def draw(self, context):
    #     layout = self.layout
    #     layout.use_property_split = True
    #     layout.use_property_decorate = False  # No animation.
    #
    #     self.definition = registry_definition.get(self.definition_id)
    #
    #     if self.definition is None:
    #         return
    #
    #     parameter = self.definition.get_parameter(self.parameter_id)
    #
    #     if parameter is None:
    #         layout.label(text="Unknown parameter", icon="ERROR")
    #         return
    #
    #     for option in parameter.options:
    #         op = layout.operator("ubk.custom_baker_parameter_set_enum", text=option.label)
    #
    #         op.parameter_id = parameter.identifier
    #         op.value = option.identifier

    def execute(
        self,
        context,
    ):
        print(self.parameter_id, self.value)
        return {"FINISHED"}


classes = (
    UBK_OT_CustomBakerParameterEnum,
    UBK_OT_CustomBakerParameterEnumOptions,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
