from __future__ import annotations


# custom_bakers/metadata_loader.py

from __future__ import annotations

import json
from typing import Any

import bpy

from .metadata import (
    BindingMetadata,
    CustomBakerMetadata,
    MetadataNotFoundError,
    MetadataParseError,
    MetadataValidationError,
    ParameterMetadata,
    METADATA_TEXT_NAME,
    CURRENT_METADATA_VERSION,
)

from ..parameter.parameter import BakerParameterOption


class MetadataLoader:
    def __init__(self, text_name: str = METADATA_TEXT_NAME):
        self.text_name = text_name

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self, text: bpy.types.Text | None = None) -> CustomBakerMetadata:
        """
        Load Custom Baker metadata from a Blender Text datablock.

        If `text` is omitted, the default UBK_BAKER_METADATA
        datablock is used.
        """

        if text is None:
            text = self._find_text()

        assert text is not None

        raw = self._read_text(text)
        data = self._parse_json(raw, text.name)

        return self._parse_metadata(data, text.name)

    # ------------------------------------------------------------------
    # Text
    # ------------------------------------------------------------------

    def _find_text(self) -> bpy.types.Text:
        text = bpy.data.texts.get(self.text_name)

        if text is None:
            raise MetadataNotFoundError(f"Custom Baker metadata text '{self.text_name}' was not found.")

        return text

    @staticmethod
    def _read_text(text: bpy.types.Text) -> str:

        try:
            return text.as_string()

        except ReferenceError as exc:
            raise MetadataNotFoundError("The metadata Text datablock is no longer valid.") from exc

    # ------------------------------------------------------------------
    # JSON
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_json(source: str, text_name: str) -> dict[str, Any]:

        try:
            data = json.loads(source)

        except json.JSONDecodeError as exc:
            raise MetadataParseError(
                f"Invalid JSON in '{text_name}' at line {exc.lineno}, column {exc.colno}: {exc.msg}"
            ) from exc

        if not isinstance(data, dict):
            raise MetadataValidationError(f"Metadata '{text_name}' must contain a JSON object at its root.")

        return data

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def _parse_metadata(self, data: dict[str, Any], source_name: str) -> CustomBakerMetadata:

        version = self._required_int(data, "version", source_name)

        if version > CURRENT_METADATA_VERSION:
            raise MetadataValidationError(
                f"Metadata '{source_name}' uses "
                f"version {version}, but this version "
                f"of Universal Baker only supports "
                f"version {CURRENT_METADATA_VERSION}."
            )

        name = self._required_string(data, "name", source_name)
        id = self._required_string(data, "id", source_name)
        prototype = self._required_string(data, "prototype", source_name)
        description = self._optional_string(data, "description", "")

        raw_parameters = data.get("parameters", [])

        if not isinstance(
            raw_parameters,
            list,
        ):
            raise MetadataValidationError(f"'parameters' in '{source_name}' must be an array.")

        parameters = tuple(
            self._parse_parameter(parameter, source_name, index) for index, parameter in enumerate(raw_parameters)
        )

        self._validate_unique_parameter_ids(parameters, source_name)

        known_keys = {
            "version",
            "name",
            "description",
            "prototype",
            "parameters",
        }

        extra = {key: value for key, value in data.items() if key not in known_keys}

        return CustomBakerMetadata(
            id=id,
            version=version,
            name=name,
            prototype=prototype,
            description=description,
            parameters=parameters,
            extra=extra,
        )

    def _parse_parameter(self, data: Any, source_name: str, index: int) -> ParameterMetadata:

        location = f"{source_name}:parameters[{index}]"

        if not isinstance(data, dict):
            raise MetadataValidationError(f"{location} must be an object.")

        identifier = self._required_string(data, "id", location)
        name = self._required_string(data, "name", location)
        parameter_type = self._required_string(data, "type", location).upper()

        allowed_types = {
            "FLOAT",
            "INT",
            "BOOL",
            "ENUM",
        }

        if parameter_type not in allowed_types:
            raise MetadataValidationError(
                f"{location}.type contains unsupported "
                f"type '{parameter_type}'. "
                f"Expected one of: "
                f"{', '.join(sorted(allowed_types))}."
            )

        default = data.get("default", None)

        description = self._optional_string(data, "description", "")
        unit = self._optional_string(data, "unit", None)
        category = self._optional_string(data, "category", None)
        order = self._optional_int(data, "order", 0)
        visible = self._optional_bool(data, "visible", True)
        min_value = self._optional_number(data, "min", None)
        max_value = self._optional_number(data, "max", None)
        soft_min = self._optional_number(data, "soft_min", None)
        soft_max = self._optional_number(data, "soft_max", None)
        options = self._parse_options(data.get("options", []), location)
        bindings = self._parse_bindings(data.get("bindings", []), location)

        return ParameterMetadata(
            identifier=identifier,
            name=name,
            type=parameter_type,
            default=default,
            description=description,
            min_value=min_value,
            max_value=max_value,
            soft_min=soft_min,
            soft_max=soft_max,
            unit=unit,
            category=category,
            order=order,
            visible=visible,
            options=tuple(options),
            bindings=tuple(bindings),
        )

    def _parse_options(self, raw_options: Any, location: str) -> list[BakerParameterOption]:

        if not isinstance(raw_options, list):
            raise MetadataValidationError(f"{location}.options must be an array.")

        options = []

        for index, raw_option in enumerate(raw_options):
            option_location = f"{location}.options[{index}]"

            if not isinstance(raw_option, dict):
                raise MetadataValidationError(f"{option_location} must be an object.")

            identifier = self._required_string(raw_option, "id", option_location)
            name = self._required_string(raw_option, "name", option_location)
            description = self._optional_string(raw_option, "description", "")

            options.append(
                BakerParameterOption(
                    identifier=identifier,
                    label=name,
                    description=description,
                )
            )

        identifiers = [option.identifier for option in options]

        if len(identifiers) != len(set(identifiers)):
            raise MetadataValidationError(f"{location}.options contains duplicate identifiers.")

        return options

    def _parse_bindings(self, raw_bindings: Any, location: str) -> list[BindingMetadata]:

        if not isinstance(raw_bindings, list):
            raise MetadataValidationError(f"{location}.bindings must be an array.")

        bindings = []

        for index, raw_binding in enumerate(raw_bindings):
            binding_location = f"{location}.bindings[{index}]"

            if not isinstance(
                raw_binding,
                dict,
            ):
                raise MetadataValidationError(f"{binding_location} must be an object.")

            binding_type = self._required_string(raw_binding, "type", binding_location).upper()

            known_keys = {
                "type",
                "material",
                "node",
                "socket",
                "modifier",
                "property",
            }

            extra = {key: value for key, value in raw_binding.items() if key not in known_keys}

            bindings.append(
                BindingMetadata(
                    binding_type=binding_type,
                    material=self._optional_string(raw_binding, "material", None),
                    node=self._optional_string(raw_binding, "node", None),
                    socket=self._optional_string(raw_binding, "socket", None),
                    modifier=self._optional_string(raw_binding, "modifier", None),
                    property=self._optional_string(raw_binding, "property", None),
                    extra=extra,
                )
            )

        return bindings

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _required_string(data: dict[str, Any], key: str, location: str) -> str:
        value = data.get(key)

        if not isinstance(value, str):
            raise MetadataValidationError(f"{location}.{key} must be a string.")

        if not value.strip():
            raise MetadataValidationError(f"{location}.{key} cannot be empty.")

        return value

    @staticmethod
    def _optional_string(data: dict[str, Any], key: str, default: str | None) -> str:
        value = data.get(key, default)

        if value is None:
            return ""

        if not isinstance(value, str):
            raise MetadataValidationError(f"'{key}' must be a string.")

        return value

    @staticmethod
    def _required_int(data: dict[str, Any], key: str, location: str) -> int:
        value = data.get(key)

        if isinstance(value, bool) or not isinstance(value, int):
            raise MetadataValidationError(f"{location}.{key} must be an integer.")

        return value

    @staticmethod
    def _optional_int(data: dict[str, Any], key: str, default: int) -> int:
        value = data.get(key, default)

        if isinstance(value, bool) or not isinstance(value, int):
            raise MetadataValidationError(f"'{key}' must be an integer.")

        return value

    @staticmethod
    def _optional_bool(data: dict[str, Any], key: str, default: bool) -> bool:
        value = data.get(key, default)

        if not isinstance(value, bool):
            raise MetadataValidationError(f"'{key}' must be a boolean.")

        return value

    @staticmethod
    def _optional_number(data: dict[str, Any], key: str, default):
        value = data.get(key, default)

        if value is None:
            return None

        if isinstance(value, bool):
            raise MetadataValidationError(f"'{key}' must be a number.")

        if not isinstance(value, (int, float)):
            raise MetadataValidationError(f"'{key}' must be a number.")

        return value

    @staticmethod
    def _validate_unique_parameter_ids(parameters: tuple[ParameterMetadata, ...], source_name: str) -> None:
        identifiers = [parameter.identifier for parameter in parameters]
        duplicates = {identifier for identifier in identifiers if identifiers.count(identifier) > 1}

        if duplicates:
            names = ", ".join(sorted(duplicates))

            raise MetadataValidationError(
                f"Metadata '{source_name}' contains duplicate parameter identifiers: {names}."
            )
