from __future__ import annotations

from ..bakers.parameter.parameter import (
    BakerParameter,
    BakerParameterType,
)
from ..services.parameter_service import (
    ParameterService,
)


class BakerParameterUI:
    @classmethod
    def draw(cls, layout, parameters: dict[str, BakerParameter], values):
        visible = [parameter for parameter in parameters.values() if parameter.visible]

        visible.sort(key=lambda parameter: parameter.order)

        categories = {}

        for parameter in visible:
            category = parameter.category or ""

            categories.setdefault(category, []).append(parameter)

        for category, category_parameters in categories.items():
            if category:
                box = layout.box()
                box.label(text=category)
                cls._draw_parameters(box, category_parameters, values)

            else:
                cls._draw_parameters(layout, category_parameters, values)

    @classmethod
    def _draw_parameters(cls, layout, parameters, values):
        for parameter in parameters:
            property_value = ParameterService.find_value(
                values,
                parameter.identifier,
            )

            if property_value is None:
                continue

            row = layout.row()
            row.label(text=parameter.name)
            cls._draw_value(row, parameter, property_value)

            if parameter.description:
                row = layout.row()
                row.label(text=parameter.description, icon="INFO")

    @staticmethod
    def _draw_value(layout, parameter, value):
        match parameter.type:
            case BakerParameterType.FLOAT:
                layout.prop(value, "float_value", text="")

            case BakerParameterType.INT:
                layout.prop(value, "int_value", text="")

            case BakerParameterType.BOOL:
                layout.prop(value, "bool_value", text="")

            case BakerParameterType.ENUM:
                # MVP:
                #
                # enum_value is a StringProperty.
                #
                # We will replace this with a proper
                # dynamic menu once the asset-side
                # parameter discovery is implemented.

                layout.prop(value, "enum_value", text="")
