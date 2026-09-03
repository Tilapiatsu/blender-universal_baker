from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from .parameter import BakerParameterOption


METADATA_TEXT_NAME = "UBK_BAKER_METADATA"

CURRENT_METADATA_VERSION = 1


class MetadataError(RuntimeError):
    """Base error for Custom Baker metadata."""


class MetadataNotFoundError(MetadataError):
    """The metadata datablock does not exist."""


class MetadataParseError(MetadataError):
    """The metadata contains invalid JSON."""


class MetadataValidationError(MetadataError):
    """The metadata has an invalid structure or value."""


@dataclass(frozen=True)
class BindingMetadata:
    """
    Describes where a parameter should be applied.

    This class intentionally does not know anything about
    Blender or ParameterBinding.
    """

    binding_type: str

    # Material socket binding
    material: str | None = None
    node: str | None = None
    socket: str | None = None

    # Modifier property binding
    modifier: str | None = None

    # Scene property Binding
    scene: str | None = None
    property: str | None = None

    # Additional binding-specific information can be kept
    # here without changing the metadata format.
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ParameterMetadata:
    """
    Declarative description of one Custom Baker parameter.

    This is deliberately NOT a BakerParameter.

    BakerParameter is the runtime representation.
    ParameterMetadata represents what was authored in baker.blend.
    """

    identifier: str
    name: str
    type: str
    default: Any = None
    description: str = ""

    min_value: float | int | None = None
    max_value: float | int | None = None

    soft_min: float | int | None = None
    soft_max: float | int | None = None

    unit: str | None = None
    category: str | None = None
    order: int = 0
    visible: bool = True
    options: tuple[BakerParameterOption, ...] = ()
    bindings: tuple[BindingMetadata, ...] = ()


@dataclass(frozen=True)
class LocalBakerMetadata:
    """
    Complete metadata description of a Local Baker asset.
    """

    id: str
    name: str
    description: str = ""
    parameters: tuple[ParameterMetadata, ...] = ()

    # Allows us to add non-breaking metadata later.
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CustomBakerMetadata:
    """
    Complete metadata description of a Custom Baker asset.
    """

    id: str
    version: int
    name: str
    prototype: str
    bake_colorspace: str
    image_colorspace: str

    display_device: str
    view_transform: str
    look: str

    exposure: float
    gamma: float

    description: str = ""
    parameters: tuple[ParameterMetadata, ...] = ()

    # Allows us to add non-breaking metadata later.
    extra: dict[str, Any] = field(default_factory=dict)
