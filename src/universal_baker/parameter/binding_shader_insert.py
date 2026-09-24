from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import bpy

from universal_baker.constant import LOG

from .binding import (
    ParameterBinding,
    ParameterBindingError,
)
from .parameter_context import ParameterContext

LOG_SCOPE = "Shader Insert Binding"


@dataclass
class ShaderInsertBinding(ParameterBinding):
    parameter_id: str

    node_name: str
    socket_input_name: str
    socket_output_name: str

    material_name: str | None = None

    def apply(self, value: Any, context: ParameterContext) -> None:
        materials = context.materials

        if materials is None:
            raise ParameterBindingError(f"Material not found for parameter '{self.parameter_id}'.")

        for material in materials:
            if materials is None:
                raise ParameterBindingError(f"Material not found for parameter '{self.parameter_id}'.")

            if not material.use_nodes:
                raise ParameterBindingError(f"Material '{material.name}' does not use nodes.")

            node_tree = material.node_tree
            node = node_tree.nodes.get(self.node_name)

            if node is None:
                raise ParameterBindingError(f"Node '{self.node_name}' not found in material '{material.name}'.")

            socket_input = node.inputs.get(self.socket_input_name)
            socket_output = node.outputs.get(self.socket_output_name)

            if socket_input is None:
                raise ParameterBindingError(
                    f"Input socket '{self.socket_input_name}' not found on node '{self.node_name}'."
                )

            if socket_output is None:
                raise ParameterBindingError(
                    f"Input socket '{self.socket_output_name}' not found on node '{self.node_name}'."
                )

            material_output = self._get_material_output(material)

            if material_output is None:
                raise ParameterBindingError(f"Material '{self.material_name}' have no material output node.")

            surface_input_socket = material_output.inputs.get("Surface")
            shader_output_socket = surface_input_socket.links[0].to_socket

            node_tree.links.new(shader_output_socket, socket_input)
            node_tree.links.new(socket_output, surface_input_socket)

    def _resolve_material(self, context: ParameterContext) -> bpy.types.Material:
        if self.material_name:
            return bpy.data.materials.get(self.material_name)

        return context.materials

    def _get_material_output(self, material) -> bpy.types.Node | None:
        for n in material.nodes:
            if n.type == "OUTPUT_MATERIAL":
                return n
