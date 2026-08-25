from __future__ import annotations

from typing import Any, TypeAlias

from ..custom_bakers.definition import CustomBakerDefinition
from ..parameter.parameter import BakerParameter, BakerParameterType, ParameterSnapshot
from ..properties.custom_baker import UBK_CustomBaker
from ..properties.baker_parameter import UBK_BakerParameterValue


class ParameterServiceError(RuntimeError):
    pass


class ParameterService:
    @classmethod
    def snapshot(cls, definition: CustomBakerDefinition, state: UBK_CustomBaker) -> ParameterSnapshot:
        """
        Create an immutable-in-practice runtime snapshot of all
        current parameter values.

        The returned dictionary contains only plain Python values and
        has no dependency on Blender RNA.

        Example:

            {
                "radius": 0.5,
                "strength": 2.0,
                "samples": 16,
                "mode": "ACCURATE",
            }

        Missing parameters are automatically initialized from the
        definition defaults.
        """

        cls.synchronize(definition, state)

        snapshot: dict[str, Any] = {}

        for parameter in definition.parameters:
            snapshot[parameter.identifier] = cls.snapshot_parameter(definition, state, parameter.identifier)

        return snapshot

    @classmethod
    def snapshot_parameter(cls, definition: CustomBakerDefinition, state: UBK_CustomBaker, parameter_id: str) -> Any:
        """
        Return one validated parameter value as a plain Python value.
        """

        parameter = definition.require_parameter(parameter_id)
        item = cls.find(state, parameter_id)

        if item is None:
            cls.synchronize(definition, state)
            item = cls.find(state, parameter_id)

        if item is None:
            raise ParameterServiceError(f"Parameter '{parameter_id}' could not be initialized.")

        value = cls._get_value(item, parameter)
        return cls._validate_value(parameter, value)

    @classmethod
    def synchronize(cls, definition: CustomBakerDefinition, state: UBK_CustomBaker) -> None:
        """
        Synchronize persistent parameter storage with
        the current CustomBakerDefinition.

        Existing values are preserved.

        New parameters receive their definition defaults.
        Removed parameters are removed from persistent storage.
        """

        # TODO: Need to take into account the case where after an updated version of an asset, the two types are
        # incompatible ( Int vs float for exemple ) -> The value should fallback to the default of the newest version
        existing = {item.identifier: item for item in state.parameters}

        valid_ids = {parameter.identifier for parameter in definition.parameters}

        # Add missing parameters.

        for parameter in definition.parameters:
            if parameter.identifier in existing:
                continue

            item = state.parameters.add()
            item.identifier = parameter.identifier
            cls._set_value(item, parameter, parameter.default)

        # Remove parameters no longer present.

        for index in reversed(range(len(state.parameters))):
            item = state.parameters[index]

            if item.identifier not in valid_ids:
                state.parameters.remove(index)

        state.asset_id = definition.identifier
        state.asset_version = definition.version

    @classmethod
    def get(cls, definition: CustomBakerDefinition, state: UBK_CustomBaker, parameter_id: str) -> Any:
        return cls.snapshot_parameter(definition, state, parameter_id)

    @classmethod
    def set(cls, definition: CustomBakerDefinition, state: UBK_CustomBaker, parameter_id: str, value: Any) -> None:
        parameter = definition.require_parameter(parameter_id)
        item = cls.find(state, parameter_id)

        if item is None:
            cls.synchronize(definition, state)
            item = cls.find(state, parameter_id)

        if item is None:
            raise ParameterServiceError(f"Parameter '{parameter_id}' could not be created.")

        value = cls._validate_value(parameter, value)
        cls._set_value(item, parameter, value)

    @staticmethod
    def find(state: UBK_CustomBaker, parameter_id: str) -> UBK_BakerParameterValue | None:

        for item in state.parameters:
            if item.identifier == parameter_id:
                return item

        return None

    @staticmethod
    def _get_value(item: UBK_BakerParameterValue, parameter: BakerParameter):

        parameter_type = parameter.parameter_type

        if parameter_type is BakerParameterType.FLOAT:
            return item.float_value

        if parameter_type is BakerParameterType.INT:
            return item.int_value

        if parameter_type is BakerParameterType.BOOL:
            return item.bool_value

        if parameter_type is BakerParameterType.ENUM:
            return item.string_value

        raise ParameterServiceError(f"Unsupported parameter type: {parameter_type}")

    @staticmethod
    def _set_value(item: UBK_BakerParameterValue, parameter: BakerParameter, value) -> None:

        parameter_type = parameter.parameter_type

        if parameter_type is BakerParameterType.FLOAT:
            item.float_value = float(value)
            return

        if parameter_type is BakerParameterType.INT:
            item.int_value = int(value)
            return

        if parameter_type is BakerParameterType.BOOL:
            item.bool_value = bool(value)
            return

        if parameter_type is BakerParameterType.ENUM:
            item.string_value = str(value)
            return

        raise ParameterServiceError(f"Unsupported parameter type: {parameter_type}")

    @classmethod
    def _validate_value(cls, parameter: BakerParameter, value):
        """
        Validate a value against the definition.

        The PropertyGroup is only storage.
        The definition remains the source of truth.
        """

        parameter_type = parameter.parameter_type

        if parameter_type is BakerParameterType.FLOAT:
            value = float(value)

            if parameter.min_value is not None:
                value = max(parameter.min_value, value)

            if parameter.max_value is not None:
                value = min(parameter.max_value, value)

            return value

        if parameter_type is BakerParameterType.INT:
            value = int(value)

            if parameter.min_value is not None:
                value = max(parameter.min_value, value)

            if parameter.max_value is not None:
                value = min(parameter.max_value, value)

            return value

        if parameter_type is BakerParameterType.BOOL:
            return bool(value)

        if parameter_type is BakerParameterType.ENUM:
            value = str(value)

            valid = {option.identifier for option in parameter.options}

            if value not in valid:
                raise ParameterServiceError(f"Invalid value '{value}' for ENUM parameter '{parameter.identifier}'.")

            return value

        raise ParameterServiceError(f"Unsupported parameter type: {parameter_type}")
