from __future__ import annotations

from typing import Any

from ..properties.baker_parameter import UBK_BakerParameterValue

from ..bakers.parameter.parameter import (
    BakerParameter,
    BakerParameterType,
)
from ..bakers.parameter.binding import (
    ParameterBinding,
)
from ..bakers.parameter.parameter_context import (
    ParameterContext,
)


class ParameterService:
    @staticmethod
    def find_value(values, parameter_id: str):
        for value in values:
            if value.identifier == parameter_id:
                return value

        return None

    @classmethod
    def ensure_value(cls, values, parameter: BakerParameter):
        value = cls.find_value(
            values,
            parameter.identifier,
        )

        if value is None:
            value = values.add()

            value.identifier = parameter.identifier

            cls.set_value(
                parameter,
                value,
                parameter.default,
            )

        return value

    @staticmethod
    def get_value(parameter: BakerParameter, property_value: UBK_BakerParameterValue) -> Any:

        match parameter.parameter_type:
            case BakerParameterType.FLOAT:
                return property_value.float_value

            case BakerParameterType.INT:
                return property_value.int_value

            case BakerParameterType.BOOL:
                return property_value.bool_value

            case BakerParameterType.ENUM:
                return property_value.enum_value

            case _:
                raise ValueError(f"Unsupported parameter type: {parameter.type}")

    @staticmethod
    def set_value(parameter: BakerParameter, property_value: UBK_BakerParameterValue, value: Any) -> None:
        value = parameter.normalize_value(value)

        if not parameter.validate_value(value):
            raise ValueError(f"Invalid value {value!r} for parameter '{parameter.identifier}'.")

        match parameter.parameter_type:
            case BakerParameterType.FLOAT:
                property_value.float_value = value

            case BakerParameterType.INT:
                property_value.int_value = value

            case BakerParameterType.BOOL:
                property_value.bool_value = value

            case BakerParameterType.ENUM:
                property_value.enum_value = value

            case _:
                raise ValueError(f"Unsupported parameter type: {parameter.type}")

    @classmethod
    def get_values(cls, parameters, properties) -> dict[str, Any]:

        result = {}

        for identifier, parameter in parameters.items():
            property_value = cls.find_value(properties, identifier)

            if property_value is None:
                continue

            result[identifier] = cls.get_value(parameter, property_value)

        return result

    @classmethod
    def apply(
        cls,
        parameters: dict[str, BakerParameter],
        values,
        bindings: dict[str, list[ParameterBinding]],
        context: ParameterContext,
    ) -> None:

        for parameter_id, parameter in parameters.items():
            property_value = cls.find_value(values, parameter_id)

            if property_value is None:
                property_value = cls.ensure_value(values, parameter)

            value = cls.get_value(parameter, property_value)

            parameter_bindings = bindings.get(parameter_id, ())

            for binding in parameter_bindings:
                binding.apply(value, context)
