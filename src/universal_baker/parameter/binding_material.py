from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import bpy
from .parameter_context import ParameterContext

from .binding import (
    ParameterBinding,
    ParameterBindingError,
)


@dataclass
class MaterialSocketBinding(ParameterBinding):
    parameter_id: str

    node_name: str
    socket_name: str

    material_name: str | None = None

    def apply(self, value: Any, context: ParameterContext) -> None:
        material = self._resolve_material(context)

        if material is None:
            raise ParameterBindingError(f"Material not found for parameter '{self.parameter_id}'.")

        if not material.use_nodes:
            raise ParameterBindingError(f"Material '{material.name}' does not use nodes.")

        node = material.node_tree.nodes.get(self.node_name)

        if node is None:
            raise ParameterBindingError(f"Node '{self.node_name}' not found in material '{material.name}'.")

        socket = node.inputs.get(self.socket_name)

        if socket is None:
            raise ParameterBindingError(f"Input socket '{self.socket_name}' not found on node '{self.node_name}'.")

        try:
            socket.default_value = value
        except (TypeError, ValueError) as exc:
            raise ParameterBindingError(
                f"Unable to assign value {value!r} to '{self.node_name}.{self.socket_name}'."
            ) from exc

    def _resolve_material(self, context: ParameterContext):
        if self.material_name:
            return bpy.data.materials.get(self.material_name)

        return context.material
