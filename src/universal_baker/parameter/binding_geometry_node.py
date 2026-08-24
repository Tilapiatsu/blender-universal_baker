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
class GeometryNodeInputBinding(ParameterBinding):
    parameter_id: str

    node_name: str
    socket_identifier: str

    modifier_name: str | None = None

    def apply(self, value: Any, context: ParameterContext) -> None:
        node_group = self._resolve_node_group(context)

        if node_group is None:
            raise ParameterBindingError(f"Node Group not found for parameter '{self.parameter_id}'.")

        node = node_group.node_tree.nodes.get(self.node_name)

        if node is None:
            raise ParameterBindingError(f"Node '{self.node_name}' not found in material '{node_group.name}'.")

        socket = node.inputs.get(self.socket_identifier)

        if socket is None:
            raise ParameterBindingError(
                f"Input socket '{self.socket_identifier}' not found on node '{self.node_name}'."
            )

        try:
            socket.default_value = value
        except (TypeError, ValueError) as exc:
            raise ParameterBindingError(
                f"Unable to assign value {value!r} to '{self.node_name}.{self.socket_identifier}'."
            ) from exc

    def _resolve_node_group(self, context: ParameterContext):
        if self.modifier_name:
            modifier = context.object.modifiers.get(self.modifier_name)
            return modifier.node_group

        return context.node_group
