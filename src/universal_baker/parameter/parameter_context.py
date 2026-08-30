from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import bpy
from ..properties.baker_parameter import UBK_BakerParameterValue


@dataclass
class ParameterContext:
    """
    Objects used while resolving ParameterBindings.

    These are runtime references and must never be persisted.
    """

    object: bpy.types.Object
    materials: list[bpy.types.Material] | None = None
    ui_prop: UBK_BakerParameterValue | None = None
    scene: bpy.types.Scene | None = None
    is_dragging: bool = False

    # Gives bindings an escape hatch for more complex assets.
    data: dict[str, Any] | None = None

    def get_data(self, key: str, default: Any = None) -> Any:
        if self.data is None:
            return default
        return self.data.get(key, default)
