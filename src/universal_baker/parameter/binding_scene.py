from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..constant import LOG
from .binding import ParameterBinding, ParameterBindingError
from .parameter_context import ParameterContext

LOG_SCOPE = "Scene Binding"


@dataclass
class ScenePropertyBinding(ParameterBinding):
    parameter_id: str

    scene_name: str
    property_path: str

    def apply(self, value: Any, context: ParameterContext) -> None:

        scene = context.scene

        if scene is None:
            raise ParameterBindingError(f"Scene '{self.scene_name}' not found.")

        self._set_property(scene, self.property_path, value)

    def _set_property(self, target, path: str, value: Any) -> None:
        parts = path.split(".")

        current = target

        for part in parts[:-1]:
            try:
                current = getattr(current, part)
            except AttributeError as exc:
                raise ParameterBindingError(f"Property path '{path}' cannot be resolved.") from exc

        final = parts[-1]

        if not hasattr(current, final):
            raise ParameterBindingError(f"Property '{path}' does not exist.")

        try:
            with LOG.scope(LOG_SCOPE):
                LOG.debug(f"Binding {value} to {final}")

            setattr(current, final, value)

        except (TypeError, ValueError) as exc:
            raise ParameterBindingError(f"Unable to assign {value!r} to '{path}'.") from exc
