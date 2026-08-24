from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .parameter_context import ParameterContext


class ParameterBindingError(RuntimeError):
    pass


class ParameterBinding(ABC):
    """
    Connects a BakerParameter to something in the temporary
    bake setup.
    """

    parameter_id: str

    @abstractmethod
    def apply(self, value: Any, context: ParameterContext) -> None:
        raise NotImplementedError
