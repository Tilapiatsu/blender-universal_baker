from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import bpy
from universal_baker.constant import LOG
from .parameter_context import ParameterContext

from .binding import (
    ParameterBinding,
    ParameterBindingError,
)

LOG_SCOPE = "Material Binding"


@dataclass
class MaterialSocketBinding(ParameterBinding):
    parameter_id: str

    node_name: str
    socket_name: str

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

            node = material.node_tree.nodes.get(self.node_name)

            if node is None:
                raise ParameterBindingError(f"Node '{self.node_name}' not found in material '{material.name}'.")

            socket = node.inputs.get(self.socket_name)

            if socket is None:
                socket = getattr(node, self.socket_name)
                if socket is None:
                    raise ParameterBindingError(
                        f"Input socket '{self.socket_name}' not found on node '{self.node_name}'."
                    )
                else:
                    setattr(node, self.socket_name, value)
            else:
                try:
                    with LOG.scope(LOG_SCOPE):
                        LOG.debug(f"Binding {value} to {self.socket_name}")
                    socket.default_value = value

                except (TypeError, ValueError) as exc:
                    raise ParameterBindingError(
                        f"Unable to assign value {value!r} to '{self.node_name}.{self.socket_name}'."
                    ) from exc

    def _resolve_material(self, context: ParameterContext) -> bpy.types.Material:
        if self.material_name:
            return bpy.data.materials.get(self.material_name)

        return context.materials
