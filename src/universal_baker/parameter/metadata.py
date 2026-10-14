from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable

import bpy

from .parameter import ParameterOption, ParameterType

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


class BindingType(StrEnum):
    MATERIAL_SOCKET = "MATERIAL_SOCKET"
    SHADER_INSERT = "SHADER_INSERT"
    MODIFIER_PROPERTY = "MODIFIER_PROPERTY"
    GEOMETRY_NODE_INPUT = "GEOMETRY_NODE_INPUT"
    SCENE_PROPERTY = "SCENE_PROPERTY"


@dataclass(frozen=True)
class BindingMetadata:
    """
    Describes where a parameter should be applied.

    This class intentionally does not know anything about
    Blender or ParameterBinding.
    """

    binding_type: BindingType

    # Material socket binding
    material: str | None = None
    node: str | None = None
    socket_input: str | None = None
    socket_output: str | None = None

    # Modifier property binding
    modifier: str | None = None

    # Scene property Binding
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
    type: ParameterType
    default: Any = None
    description: str = ""

    min_value: float | int | None = None
    max_value: float | int | None = None

    soft_min: float | int | None = None
    soft_max: float | int | None = None

    unit: str = "NONE"
    subtype: str = "NONE"
    category: str | None = None
    order: int = 0
    visible: bool = True
    options: tuple[ParameterOption, ...] = ()
    bindings: tuple[BindingMetadata, ...] = ()

    def blender_property(self, update: Callable | None = None):
        match self.type:
            case ParameterType.FLOAT:
                return bpy.props.FloatProperty(
                    name=self.name,
                    default=self.default,
                    description=self.description,
                    soft_min=self.soft_min,
                    soft_max=self.soft_max,
                    min=self.min_value,
                    max=self.max_value,
                    unit=self.unit,
                    subtype=self.subtype,
                    update=update,
                )
            case ParameterType.BOOL:
                return bpy.props.BoolProperty(
                    name=self.name,
                    default=self.default,
                    description=self.description,
                    update=update,
                )
            case ParameterType.INT:
                return bpy.props.IntProperty(
                    name=self.name,
                    default=self.default,
                    description=self.description,
                    soft_min=self.soft_min,
                    soft_max=self.soft_max,
                    min=self.min_value,
                    max=self.max_value,
                    unit=self.unit,
                    subtype=self.subtype,
                    update=update,
                )
            case ParameterType.STRING:
                return bpy.props.StringProperty(
                    name=self.name,
                    default=self.default,
                    description=self.description,
                    update=update,
                )
            case ParameterType.VECTOR:
                return bpy.props.FloatVectorProperty(
                    name=self.name,
                    default=self.default,
                    description=self.description,
                    soft_min=self.soft_min,
                    soft_max=self.soft_max,
                    min=self.min_value,
                    max=self.max_value,
                    unit=self.unit,
                    subtype=self.subtype,
                    update=update,
                )
            case ParameterType.OBJ:
                return bpy.props.PointerProperty(
                    name=self.name,
                    description=self.description,
                    type=bpy.types.Object,
                    update=update,
                )
            case ParameterType.SHADER:
                return bpy.props.StringProperty(
                    name=self.name,
                    default=self.default,
                    description=self.description,
                    update=update,
                )
            case ParameterType.ENUM:
                items = [(o.identifier, o.label, o.description) for o in self.options]
                return bpy.props.EnumProperty(
                    name=self.name,
                    default=self.default,
                    description=self.description,
                    items=items,
                    update=update,
                )


@dataclass(frozen=True)
class MetadataBase: ...


@dataclass(frozen=True)
class LocalMetadata(MetadataBase):
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
class CustomBakerMetadata(MetadataBase):
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
