from __future__ import annotations

from collections.abc import Callable

from universal_baker.parameter.binding_scene import ScenePropertyBinding

from .binding import ParameterBinding
from .binding_geometry_node import GeometryNodeInputBinding
from .binding_material import MaterialSocketBinding
from .binding_modifier import ModifierPropertyBinding
from .metadata import (
    BindingMetadata,
)


class BindingFactoryError(RuntimeError):
    """Base error raised while creating parameter bindings."""


BindingCreator = Callable[[str, BindingMetadata], ParameterBinding]


class BindingFactory:
    def __init__(self):
        self._creators: dict[str, BindingCreator] = {
            "MATERIAL_SOCKET": self._create_material_socket,
            "MODIFIER_PROPERTY": self._create_modifier_property,
            "GEOMETRY_NODE_INPUT": self._create_geometry_node_input,
            "SCENE_PROPERTY": self._create_scene_input,
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create(self, parameter_id: str, metadata: BindingMetadata) -> ParameterBinding:
        binding_type = metadata.binding_type.upper()

        creator = self._creators.get(binding_type)

        if creator is None:
            raise BindingFactoryError(
                f"Unsupported binding type '{metadata.binding_type}' for parameter '{parameter_id}'."
            )

        return creator(parameter_id, metadata)

    def create_many(
        self,
        parameter_id: str,
        metadata: list[BindingMetadata] | tuple[BindingMetadata, ...],
    ) -> list[ParameterBinding]:
        return [self.create(parameter_id, binding) for binding in metadata]

    def register(
        self,
        binding_type: str,
        creator: BindingCreator,
    ) -> None:

        binding_type = binding_type.upper()

        if binding_type in self._creators:
            raise BindingFactoryError(f"Binding type '{binding_type}' is already registered.")

        self._creators[binding_type] = creator

    # ------------------------------------------------------------------
    # Material
    # ------------------------------------------------------------------

    def _create_material_socket(self, parameter_id: str, metadata: BindingMetadata) -> ParameterBinding:

        material = self._require(
            metadata.material,
            "material",
            parameter_id,
            "MATERIAL_SOCKET",
        )

        node = self._require(
            metadata.node,
            "node",
            parameter_id,
            "MATERIAL_SOCKET",
        )

        socket = self._require(
            metadata.socket,
            "socket",
            parameter_id,
            "MATERIAL_SOCKET",
        )

        return MaterialSocketBinding(
            parameter_id=parameter_id,
            material_name=material,
            node_name=node,
            socket_name=socket,
        )

    # ------------------------------------------------------------------
    # Modifier
    # ------------------------------------------------------------------

    def _create_modifier_property(self, parameter_id: str, metadata: BindingMetadata) -> ParameterBinding:
        modifier = self._require(
            metadata.modifier,
            "modifier",
            parameter_id,
            "MODIFIER_PROPERTY",
        )

        property = self._require(
            metadata.property,
            "property",
            parameter_id,
            "MODIFIER_PROPERTY",
        )

        return ModifierPropertyBinding(
            parameter_id=parameter_id,
            modifier_name=modifier,
            property_path=property,
        )

    # ------------------------------------------------------------------
    # Geometry Nodes
    # ------------------------------------------------------------------

    def _create_geometry_node_input(self, parameter_id: str, metadata: BindingMetadata) -> ParameterBinding:
        modifier = self._require(
            metadata.modifier,
            "modifier",
            parameter_id,
            "GEOMETRY_NODE_INPUT",
        )

        socket = self._require(
            metadata.socket,
            "socket",
            parameter_id,
            "GEOMETRY_NODE_INPUT",
        )

        node = self._require(
            metadata.node,
            "node",
            parameter_id,
            "GEOMETRY_NODE_INPUT",
        )

        return GeometryNodeInputBinding(
            parameter_id=parameter_id,
            node_name=node,
            modifier_name=modifier,
            socket_identifier=socket,
        )

    def _create_scene_input(self, parameter_id: str, metadata: BindingMetadata) -> ParameterBinding:
        scene = self._require(
            metadata.scene,
            "scene",
            parameter_id,
            "SCENE_PROPERTY",
        )

        property = self._require(
            metadata.property,
            "property",
            parameter_id,
            "SCENE_PROPERTY",
        )

        return ScenePropertyBinding(
            parameter_id=parameter_id,
            scene_name=scene,
            property_path=property,
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def _require(
        value: str | None,
        field_name: str,
        parameter_id: str,
        binding_type: str,
    ) -> str:

        if not value:
            raise BindingFactoryError(f"{binding_type} binding for parameter '{parameter_id}' requires '{field_name}'.")

        return value
