from __future__ import annotations

import json
from typing import Any
from pathlib import Path

import bpy
from .definition import CustomBakerDefinition
from ...constant import LOG

from ..metadata import (
    BindingMetadata,
    CustomBakerMetadata,
    MetadataNotFoundError,
    MetadataParseError,
    MetadataValidationError,
    ParameterMetadata,
    METADATA_TEXT_NAME,
    CURRENT_METADATA_VERSION,
)

from ..parameter import BakerParameterOption


class MetadataLoaderError(RuntimeError):
    """Base exception for metadata loading errors."""


class MetadataLoader:
    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @classmethod
    def load(cls, asset_path: Path) -> CustomBakerMetadata:
        """
        Load Custom Baker metadata from a Blender Text datablock.

        If `text` is omitted, the default UBK_BAKER_METADATA
        datablock is used.
        """
        asset_path = Path(asset_path)

        cls._validate_path(asset_path)

        text = cls._load_text(METADATA_TEXT_NAME, asset_path)

        try:
            raw_json = text.as_string()
            data = cls._parse_json(raw_json, METADATA_TEXT_NAME)
            return cls._parse_metadata(data, METADATA_TEXT_NAME)

        finally:
            cls._remove_text(text)

    @classmethod
    def load_definition(cls, asset_path: Path) -> CustomBakerDefinition:
        metadata = cls.load(asset_path)

        return CustomBakerDefinition.from_metadata(metadata, asset_path)

    @staticmethod
    def _validate_path(
        asset_path: Path,
    ) -> None:

        if not asset_path.exists():
            raise MetadataLoaderError(f"Custom baker asset does not exist: {asset_path}")

        if not asset_path.is_file():
            raise MetadataLoaderError(f"Custom baker asset is not a file: {asset_path}")

        if asset_path.suffix.lower() != ".blend":
            raise MetadataLoaderError(f"Custom baker asset must be a .blend file: {asset_path}")

    # ------------------------------------------------------------------
    # Text
    # ------------------------------------------------------------------
    @classmethod
    def _load_text(
        cls,
        text_name: str,
        asset_path: Path,
    ) -> bpy.types.Text:

        text = None

        LOG.debug(f"Reading Metadata from asset {asset_path}")
        with bpy.data.libraries.load(str(asset_path), link=False) as (data_from, data_to):
            if text_name not in data_from.texts:
                raise MetadataNotFoundError(f"Metadata Text datablock '{text_name}' was not found in '{asset_path}'.")

            data_to.texts = [text_name]

        # data_to.texts now contains the actual loaded Text datablock.
        #
        # We find it explicitly rather than relying on:
        #
        #     bpy.data.texts[self.text_name]
        #
        # because Blender can rename datablocks when a name collision
        # already exists in the current file.

        for text in data_to.texts:
            if text is not None:
                return text

        raise MetadataNotFoundError(f"Metadata Text datablock '{text_name}' could not be loaded from '{asset_path}'.")

    @classmethod
    def _find_text(cls, text_name: str = METADATA_TEXT_NAME) -> bpy.types.Text:
        text = bpy.data.texts.get(text_name)

        if text is None:
            raise MetadataNotFoundError(f"Custom Baker metadata text '{text_name}' was not found.")

        return text

    @staticmethod
    def _read_text(text: bpy.types.Text) -> str:

        try:
            return text.as_string()

        except ReferenceError as exc:
            raise MetadataNotFoundError("The metadata Text datablock is no longer valid.") from exc

    @staticmethod
    def _remove_text(text: bpy.types.Text) -> None:

        if text is None:
            return

        # The datablock may already have been removed by Blender
        # or by another piece of code.
        if text.name not in bpy.data.texts:
            return

        bpy.data.texts.remove(
            text,
            do_unlink=True,
        )

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

    @classmethod
    def _parse_metadata(cls, data: dict[str, Any], source_name: str) -> CustomBakerMetadata:

        version = cls._required_int(data, "version", source_name)

        if version > CURRENT_METADATA_VERSION:
            raise MetadataValidationError(
                f"Metadata '{source_name}' uses "
                f"version {version}, but this version "
                f"of Universal Baker only supports "
                f"version {CURRENT_METADATA_VERSION}."
            )

        name = cls._required_string(data, "name", source_name)
        id = cls._required_string(data, "id", source_name)
        prototype = cls._required_string(data, "prototype", source_name)
        description = cls._optional_string(data, "description", "")

        raw_parameters = data.get("parameters", [])

        if not isinstance(
            raw_parameters,
            list,
        ):
            raise MetadataValidationError(f"'parameters' in '{source_name}' must be an array.")

        parameters = tuple(
            cls._parse_parameter(parameter, source_name, index) for index, parameter in enumerate(raw_parameters)
        )

        cls._validate_unique_parameter_ids(parameters, source_name)

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

    @classmethod
    def _parse_parameter(cls, data: Any, source_name: str, index: int) -> ParameterMetadata:

        location = f"{source_name}:parameters[{index}]"

        if not isinstance(data, dict):
            raise MetadataValidationError(f"{location} must be an object.")

        identifier = cls._required_string(data, "id", location)
        name = cls._required_string(data, "name", location)
        parameter_type = cls._required_string(data, "type", location).upper()

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

        description = cls._optional_string(data, "description", "")
        unit = cls._optional_string(data, "unit", None)
        category = cls._optional_string(data, "category", None)
        order = cls._optional_int(data, "order", 0)
        visible = cls._optional_bool(data, "visible", True)
        min_value = cls._optional_number(data, "min", None)
        max_value = cls._optional_number(data, "max", None)
        soft_min = cls._optional_number(data, "soft_min", None)
        soft_max = cls._optional_number(data, "soft_max", None)
        options = cls._parse_options(data.get("options", []), location)
        bindings = cls._parse_bindings(data.get("bindings", []), location)

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

    @classmethod
    def _parse_options(cls, raw_options: Any, location: str) -> list[BakerParameterOption]:

        if not isinstance(raw_options, list):
            raise MetadataValidationError(f"{location}.options must be an array.")

        options = []

        for index, raw_option in enumerate(raw_options):
            option_location = f"{location}.options[{index}]"

            if not isinstance(raw_option, dict):
                raise MetadataValidationError(f"{option_location} must be an object.")

            identifier = cls._required_string(raw_option, "id", option_location)
            name = cls._required_string(raw_option, "name", option_location)
            description = cls._optional_string(raw_option, "description", "")

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

    @classmethod
    def _parse_bindings(cls, raw_bindings: Any, location: str) -> list[BindingMetadata]:

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

            binding_type = cls._required_string(raw_binding, "type", binding_location).upper()

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
                    material=cls._optional_string(raw_binding, "material", None),
                    node=cls._optional_string(raw_binding, "node", None),
                    socket=cls._optional_string(raw_binding, "socket", None),
                    modifier=cls._optional_string(raw_binding, "modifier", None),
                    property=cls._optional_string(raw_binding, "property", None),
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
