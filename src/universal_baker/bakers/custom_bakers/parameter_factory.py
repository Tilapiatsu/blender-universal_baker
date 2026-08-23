from __future__ import annotations

from typing import Any

from .metadata import (
    ParameterMetadata,
)

from ..parameter.parameter import (
    BakerParameter,
    BakerParameterType,
    BakerParameterOption,
)


class ParameterFactoryError(RuntimeError):
    """Base error raised while creating BakerParameter objects."""


class ParameterFactory:
    """
    Converts declarative ParameterMetadata into runtime
    BakerParameter objects.
    """

    TYPE_MAP = {
        "FLOAT": BakerParameterType.FLOAT,
        "INT": BakerParameterType.INT,
        "BOOL": BakerParameterType.BOOL,
        "ENUM": BakerParameterType.ENUM,
    }

    def create(self, metadata: ParameterMetadata) -> BakerParameter:
        parameter_type = self._get_parameter_type(metadata)

        default = self._normalize_default(
            metadata,
            parameter_type,
        )

        options = self._create_options(metadata)

        self._validate(
            metadata,
            default,
            options,
        )

        return self._create_parameter(
            metadata=metadata,
            parameter_type=parameter_type,
            default=default,
            options=options,
        )

    # ------------------------------------------------------------------
    # Type
    # ------------------------------------------------------------------

    def _get_parameter_type(self, metadata: ParameterMetadata) -> BakerParameterType:
        try:
            return self.TYPE_MAP[metadata.type.upper()]

        except KeyError as exc:
            raise ParameterFactoryError(
                f"Unsupported parameter type '{metadata.type}' for '{metadata.identifier}'."
            ) from exc

    # ------------------------------------------------------------------
    # Default
    # ------------------------------------------------------------------

    def _normalize_default(self, metadata: ParameterMetadata, parameter_type: BakerParameterType) -> Any:
        value = metadata.default

        if parameter_type is BakerParameterType.FLOAT:
            if value is None:
                return 0.0

            if isinstance(value, bool):
                raise ParameterFactoryError(f"FLOAT parameter '{metadata.identifier}' cannot have a boolean default.")

            try:
                return float(value)

            except (TypeError, ValueError) as exc:
                raise ParameterFactoryError(f"Invalid FLOAT default for '{metadata.identifier}': {value!r}") from exc

        if parameter_type is BakerParameterType.INT:
            if value is None:
                return 0

            if isinstance(value, bool):
                raise ParameterFactoryError(f"INT parameter '{metadata.identifier}' cannot have a boolean default.")

            try:
                return int(value)

            except (TypeError, ValueError) as exc:
                raise ParameterFactoryError(f"Invalid INT default for '{metadata.identifier}': {value!r}") from exc

        if parameter_type is BakerParameterType.BOOL:
            if value is None:
                return False

            if not isinstance(value, bool):
                raise ParameterFactoryError(f"BOOL parameter '{metadata.identifier}' requires a boolean default.")

            return value

        if parameter_type is BakerParameterType.ENUM:
            if value is None:
                if metadata.options:
                    return metadata.options[0].identifier

                return ""

            if not isinstance(value, str):
                raise ParameterFactoryError(f"ENUM parameter '{metadata.identifier}' requires a string default.")

            return value

        raise ParameterFactoryError(f"Unhandled parameter type '{parameter_type}'.")

    # ------------------------------------------------------------------
    # Options
    # ------------------------------------------------------------------

    @staticmethod
    def _create_options(metadata: ParameterMetadata) -> tuple[BakerParameterOption, ...]:
        return tuple(metadata.options)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self, metadata: ParameterMetadata, default: Any, options: tuple[BakerParameterOption, ...]) -> None:

        if metadata.min_value is not None and default < metadata.min_value:
            raise ParameterFactoryError(f"Default value of parameter '{metadata.identifier}' is below its minimum.")

        if metadata.max_value is not None and default > metadata.max_value:
            raise ParameterFactoryError(f"Default value of parameter '{metadata.identifier}' is above its maximum.")

        if (
            metadata.min_value is not None
            and metadata.max_value is not None
            and metadata.min_value > metadata.max_value
        ):
            raise ParameterFactoryError(f"Parameter '{metadata.identifier}' has min > max.")

        if metadata.soft_min is not None and metadata.soft_max is not None and metadata.soft_min > metadata.soft_max:
            raise ParameterFactoryError(f"Parameter '{metadata.identifier}' has soft_min > soft_max.")

        if metadata.type.upper() == "ENUM":
            identifiers = {option.identifier for option in options}

            if default not in identifiers:
                raise ParameterFactoryError(
                    f"Default value '{default}' of ENUM parameter '{metadata.identifier}' is not one of its options."
                )

    # ------------------------------------------------------------------
    # Runtime object
    # ------------------------------------------------------------------

    def _create_parameter(
        self,
        *,
        metadata: ParameterMetadata,
        parameter_type: BakerParameterType,
        default: Any,
        options: tuple[BakerParameterOption, ...],
    ) -> BakerParameter:
        """
        This is the only method that should need adaptation if
        BakerParameter's constructor changes.
        """

        return BakerParameter(
            identifier=metadata.identifier,
            name=metadata.name,
            parameter_type=parameter_type,
            default=default,
            description=metadata.description,
            min_value=metadata.min_value,
            max_value=metadata.max_value,
            soft_min=metadata.soft_min,
            soft_max=metadata.soft_max,
            unit=metadata.unit,
            category=metadata.category,
            order=metadata.order,
            visible=metadata.visible,
            options=options,
        )
