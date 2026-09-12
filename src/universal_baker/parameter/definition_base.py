from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from .binding import ParameterBinding
from .metadata import MetadataBase
from .parameter import Parameter


class DefinitionError(RuntimeError):
    """Raised when a Baker definition is invalid."""


@dataclass(frozen=True)
class DefinitionBase:
    """
    Runtime description of a Local Baker.

    A definition describes WHAT a Local Baker is capable of doing,
    but does not contain its current parameter values.

    Persistent values are managed separately by ParameterService.

    The definition is therefore safe to share between:
        - bake
        - preview
        - display
        - UI
        - validation
    """

    identifier: str
    name: str
    parameters: tuple[Parameter, ...] = ()
    bindings: dict[str, tuple[ParameterBinding, ...]] = field(default_factory=dict)
    description: str = ""
    version: int = 1
    metadata: MetadataBase | None = None

    # ------------------------------------------------------------------
    # Parameters
    # ------------------------------------------------------------------

    @property
    def parameter_map(self) -> dict[str, Parameter]:
        """
        Return parameters indexed by identifier.
        """

        return {parameter.identifier: parameter for parameter in self.parameters}

    def get_parameter(self, identifier: str) -> Parameter | None:
        """
        Return a parameter by identifier.
        """

        for parameter in self.parameters:
            if parameter.identifier == identifier:
                return parameter

        return None

    def require_parameter(self, identifier: str) -> Parameter:
        """
        Return a parameter or raise an informative error.
        """

        parameter = self.get_parameter(identifier)

        if parameter is None:
            raise DefinitionError(f"'{self.name}' has no parameter '{identifier}'.")

        return parameter

    # ------------------------------------------------------------------
    # Bindings
    # ------------------------------------------------------------------

    def get_bindings(self, parameter_id: str) -> tuple[ParameterBinding, ...]:
        """
        Return all bindings associated with a parameter.
        """

        return self.bindings.get(
            parameter_id,
            (),
        )

    def require_bindings(self, parameter_id: str) -> tuple[ParameterBinding, ...]:
        """
        Return bindings for a parameter.

        Raises if the parameter has no bindings.
        """

        bindings = self.get_bindings(parameter_id)

        if not bindings:
            raise DefinitionError(f"'{self.name}' parameter '{parameter_id}' has no bindings.")

        return bindings

    # ------------------------------------------------------------------
    # Iteration
    # ------------------------------------------------------------------

    def iter_parameters(self) -> Iterable[Parameter]:
        """
        Iterate parameters in their authored order.
        """

        return iter(self.parameters)

    def iter_bindings(
        self,
        parameter_id: str,
    ) -> Iterable[ParameterBinding]:
        """
        Iterate all bindings associated with a parameter.
        """

        return iter(self.get_bindings(parameter_id))

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> None:
        """
        Validate the internal consistency of the definition.

        This does NOT validate Blender data such as whether a material,
        node, modifier or socket actually exists.

        That belongs to CustomBakerAssetValidator.
        """

        self._validate_identity()
        self._validate_parameters()
        self._validate_bindings()

    def _validate_identity(self) -> None:

        if not self.identifier:
            raise DefinitionError("Identifier cannot be empty.")

        if not self.name:
            raise DefinitionError("Name cannot be empty.")

    def _validate_parameters(self) -> None:

        identifiers: set[str] = set()

        for parameter in self.parameters:
            identifier = parameter.identifier

            if not identifier:
                raise DefinitionError(f"'{self.name}' contains a parameter with an empty identifier.")

            if identifier in identifiers:
                raise DefinitionError(f"'{self.name}' contains duplicate parameter '{identifier}'.")

            identifiers.add(identifier)

    def _validate_bindings(self) -> None:

        parameter_ids = {parameter.identifier for parameter in self.parameters}

        for parameter_id in self.bindings:
            if parameter_id not in parameter_ids:
                raise DefinitionError(f"'{self.name}' contains bindings for unknown parameter '{parameter_id}'.")

    @classmethod
    def from_metadata(cls, *args, **kwargs) -> DefinitionBase: ...

    @staticmethod
    def _make_identifier(name: str) -> str:
        """
        Convert the authored name into a stable identifier.

        This is intentionally conservative for now.
        """

        return name.strip().lower().replace(" ", "_").replace("-", "_")
