from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import bpy

from ..constant import LOG
from .parameter_context import ParameterContext

from .binding import (
    ParameterBinding,
    ParameterBindingError,
)

LOG_SCOPE = "GeometryNode Binding"


@dataclass
class GeometryNodeInputBinding(ParameterBinding):
    parameter_id: str

    node_name: str
    socket_identifier: str

    modifier_name: str | None = None

    def apply(self, value: Any, context: ParameterContext) -> None:
        modifier = context.object.modifiers.get(self.modifier_name)

        if modifier is None:
            raise ParameterBindingError(f"Modifier not found for parameter '{self.parameter_id}'.")

        node_group = modifier.node_group

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
            with LOG.scope(LOG_SCOPE):
                LOG.debug(f"Binding {value} to {self.socket_identifier}")
            socket.default_value = value

        except (TypeError, ValueError) as exc:
            raise ParameterBindingError(
                f"Unable to assign value {value!r} to '{self.node_name}.{self.socket_identifier}'."
            ) from exc
