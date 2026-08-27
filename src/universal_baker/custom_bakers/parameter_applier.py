from __future__ import annotations

from typing import Any

from ..parameter.parameter_context import ParameterContext

from .definition import CustomBakerDefinition
from ..parameter.parameter import BakerParameterType, ParameterSnapshot


class ParameterApplyError(RuntimeError):
    """Raised when a baker parameter cannot be applied."""


class ParameterApplier:
    """
    Apply a ParameterSnapshot to a loaded custom baker asset.

    ParameterApplier is deliberately independent from Blender's
    persistent UBK_CustomBaker property groups.

    It combines:

        CustomBakerDefinition
            -> tells us WHERE parameters are bound

        ParameterSnapshot
            -> tells us WHAT values to apply

        ParameterApplyContext
            -> tells us WHICH runtime Blender datablocks to modify
    """

    @staticmethod
    def clamp_value(
        value: float | int,
        minimum: float | int,
        maximum: float | int,
    ) -> float | int:
        return max(
            minimum,
            min(value, maximum),
        )

    @classmethod
    def apply(
        cls,
        definition: CustomBakerDefinition,
        snapshot: ParameterSnapshot,
        context: ParameterContext,
    ) -> None:
        """
        Apply all parameters from ``snapshot``.

        Parameters that are present in the definition but missing
        from the snapshot are ignored.

        This is intentional because a snapshot may originate from
        an older project version or from a partial parameter set.
        """

        for parameter in definition.parameters:
            parameter_id = parameter.identifier

            if parameter_id not in snapshot:
                continue

            value = snapshot.get(parameter_id)

            # NOTE: Hard Clamp
            if value is not None and parameter.min_value is not None and parameter.max_value is not None:
                value = cls.clamp_value(value, parameter.min_value, parameter.max_value)

            # TODO: soft clamping uiprops doesn't work properly because it is not happening at the right spot. Need to make
            # sure this apply() method is happening only for the modified parameter only firt, and to move the soft clamping from  refresh_preview_parameters() method in runtime_visualization.py

            # NOTE: Soft Clamp
            if context.ui_prop is not None and parameter.soft_min is not None and parameter.soft_max is not None:
                match parameter.parameter_type:
                    case BakerParameterType.FLOAT:
                        context.ui_prop.float_value = cls.clamp_value(
                            context.ui_prop.float_value,
                            parameter.soft_min,
                            parameter.soft_max,
                        )
                    case BakerParameterType.INT:
                        context.ui_prop.int_value = cls.clamp_value(
                            context.ui_prop.int_value,
                            parameter.soft_min,
                            parameter.soft_max,
                        )
            bindings = definition.get_bindings(parameter_id)

            if bindings is None:
                continue

            binding = None

            try:
                for binding in bindings:
                    binding.apply(value=value, context=context)

            except Exception as exc:
                raise ParameterApplyError(
                    cls._format_error(
                        definition=definition,
                        parameter_id=parameter_id,
                        binding=binding,
                        value=value,
                    )
                ) from exc

    @staticmethod
    def _format_error(
        definition: CustomBakerDefinition,
        parameter_id: str,
        binding: Any,
        value: Any,
    ) -> str:
        return (
            f"Failed to apply parameter "
            f"'{parameter_id}' for custom baker "
            f"'{definition.identifier}'. "
            f"Binding={type(binding).__name__}, "
            f"value={value!r}"
        )
