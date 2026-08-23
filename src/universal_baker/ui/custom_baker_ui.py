from __future__ import annotations

from typing import Any

from ..services.parameter_service_02 import ParameterService
from ..bakers.parameter.parameter import BakerParameterType


class BakerParameterUI:
    def __init__(self, parameter_service: ParameterService):
        self.parameter_service = parameter_service

    def draw(
        self,
        layout,
        definition,
        state,
    ):
        self.parameter_service.ensure(definition, state)

        for parameter in definition.parameters:
            item = self.parameter_service.find(state, parameter.identifier)

            if item is None:
                continue

            self._draw_parameter(layout, parameter, item)

    def _draw_parameter(self, layout, parameter, item):
        parameter_type = parameter.type

        if parameter_type is BakerParameterType.FLOAT:
            layout.prop(item, "float_value", text=parameter.name)

        elif parameter_type is BakerParameterType.INT:
            layout.prop(item, "int_value", text=parameter.name)

        elif parameter_type is BakerParameterType.BOOL:
            layout.prop(item, "bool_value", text=parameter.name)

        elif parameter_type is BakerParameterType.ENUM:
            self._draw_enum(layout, parameter, item)

        # TODO: Need to write _draw_enum
