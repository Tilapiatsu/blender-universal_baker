from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, TypeAlias

ParameterSnapshot: TypeAlias = dict[str, Any]


class BakerParameterType(str, Enum):
    FLOAT = "FLOAT"
    INT = "INT"
    BOOL = "BOOL"
    ENUM = "ENUM"


@dataclass(frozen=True)
class BakerParameterOption:
    """One option of an ENUM parameter."""

    identifier: str
    label: str
    description: str = ""


@dataclass
class BakerParameter:
    """
    Definition of a parameter exposed by a baker.

    This class describes what the parameter is.

    It does NOT describe where the parameter is applied.
    That responsibility belongs to ParameterBinding.
    """

    identifier: str
    name: str

    parameter_type: BakerParameterType

    description: str = ""

    default: Any = None

    min_value: float | int | None = None
    max_value: float | int | None = None

    soft_min: float | int | None = None
    soft_max: float | int | None = None

    unit: str | None = None

    category: str | None = None

    options: tuple[BakerParameterOption, ...] = field(default_factory=tuple)

    visible: bool = True

    # Useful later for controlling ordering in the UI.
    order: int = 0

    def validate_value(self, value: Any) -> bool:
        """Validate a value against this parameter definition."""

        if self.parameter_type == BakerParameterType.FLOAT:
            if not isinstance(value, (float, int)):
                return False

        elif self.parameter_type == BakerParameterType.INT:
            if not isinstance(value, int):
                return False

        elif self.parameter_type == BakerParameterType.BOOL:
            if not isinstance(value, bool):
                return False

        elif self.parameter_type == BakerParameterType.ENUM:
            valid = {option.identifier for option in self.options}

            if value not in valid:
                return False

        else:
            return False

        if self.min_value is not None and value < self.min_value:
            return False

        if self.max_value is not None and value > self.max_value:
            return False

        return True

    def normalize_value(self, value: Any) -> Any:
        """
        Convert a value to the appropriate Python type.

        This is useful when values come from Blender properties.
        """

        if self.parameter_type == BakerParameterType.FLOAT:
            return float(value)

        if self.parameter_type == BakerParameterType.INT:
            return int(value)

        if self.parameter_type == BakerParameterType.BOOL:
            return bool(value)

        if self.parameter_type == BakerParameterType.ENUM:
            return str(value)

        raise ValueError(f"Unsupported parameter type: {self.parameter_type}")
