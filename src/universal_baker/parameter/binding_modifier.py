from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..constant import LOG

from .parameter_context import ParameterContext

from .binding import ParameterBinding, ParameterBindingError

LOG_SCOPE = "Modifier Binding"


@dataclass
class ModifierPropertyBinding(ParameterBinding):
    parameter_id: str

    modifier_name: str
    property_path: str

    def apply(self, value: Any, context: ParameterContext) -> None:

        obj = context.object

        modifier = obj.modifiers.get(self.modifier_name)

        if modifier is None:
            raise ParameterBindingError(f"Modifier '{self.modifier_name}' not found on '{obj.name}'.")

        self._set_property(modifier, self.property_path, value)

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

            setattr(
                current,
                final,
                value,
            )
        except (TypeError, ValueError) as exc:
            raise ParameterBindingError(f"Unable to assign {value!r} to '{path}'.") from exc
