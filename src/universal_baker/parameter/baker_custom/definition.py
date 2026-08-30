from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from ..binding_factory import BindingFactory
from ..parameter_factory import ParameterFactory

from ..metadata import CustomBakerMetadata

from ..parameter import BakerParameter
from ..binding import ParameterBinding


class CustomBakerDefinitionError(RuntimeError):
    """Raised when a Custom Baker definition is invalid."""


@dataclass(frozen=True)
class CustomBakerDefinition:
    """
    Runtime description of a Custom Baker.

    A definition describes WHAT a Custom Baker is capable of doing,
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
    prototype: str
    parameters: tuple[BakerParameter, ...] = ()
    bindings: dict[str, tuple[ParameterBinding, ...]] = field(default_factory=dict)
    description: str = ""
    version: int = 1
    asset_path: str | None = None
    metadata: CustomBakerMetadata | None = None

    # ------------------------------------------------------------------
    # Parameters
    # ------------------------------------------------------------------

    @property
    def parameter_map(self) -> dict[str, BakerParameter]:
        """
        Return parameters indexed by identifier.
        """

        return {parameter.identifier: parameter for parameter in self.parameters}

    def get_parameter(self, identifier: str) -> BakerParameter | None:
        """
        Return a parameter by identifier.
        """

        for parameter in self.parameters:
            if parameter.identifier == identifier:
                return parameter

        return None

    def require_parameter(self, identifier: str) -> BakerParameter:
        """
        Return a parameter or raise an informative error.
        """

        parameter = self.get_parameter(identifier)

        if parameter is None:
            raise CustomBakerDefinitionError(f"Custom Baker '{self.name}' has no parameter '{identifier}'.")

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
            raise CustomBakerDefinitionError(f"Custom Baker '{self.name}' parameter '{parameter_id}' has no bindings.")

        return bindings

    # ------------------------------------------------------------------
    # Iteration
    # ------------------------------------------------------------------

    def iter_parameters(self) -> Iterable[BakerParameter]:
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
            raise CustomBakerDefinitionError("Custom Baker identifier cannot be empty.")

        if not self.name:
            raise CustomBakerDefinitionError("Custom Baker name cannot be empty.")

        if not self.prototype:
            raise CustomBakerDefinitionError(f"Custom Baker '{self.name}' does not define a prototype.")

    def _validate_parameters(self) -> None:

        identifiers: set[str] = set()

        for parameter in self.parameters:
            identifier = parameter.identifier

            if not identifier:
                raise CustomBakerDefinitionError(
                    f"Custom Baker '{self.name}' contains a parameter with an empty identifier."
                )

            if identifier in identifiers:
                raise CustomBakerDefinitionError(
                    f"Custom Baker '{self.name}' contains duplicate parameter '{identifier}'."
                )

            identifiers.add(identifier)

    def _validate_bindings(self) -> None:

        parameter_ids = {parameter.identifier for parameter in self.parameters}

        for parameter_id in self.bindings:
            if parameter_id not in parameter_ids:
                raise CustomBakerDefinitionError(
                    f"Custom Baker '{self.name}' contains bindings for unknown parameter '{parameter_id}'."
                )

    @classmethod
    def from_metadata(
        cls,
        metadata: CustomBakerMetadata,
        asset_path: Path,
    ) -> CustomBakerDefinition:
        """
        Build a CustomBakerDefinition from the results of
        MetadataLoader, ParameterFactory and BindingFactory.
        """
        parameter_factory = ParameterFactory()
        binding_factory = BindingFactory()
        parameters: list[BakerParameter] = []
        bindings: dict[str, list[ParameterBinding]] = {}

        for m in metadata.parameters:
            parameter = parameter_factory.create(m)
            parameters.append(parameter)
            for b in m.bindings:
                binding = binding_factory.create(parameter.identifier, b)
                if parameter.identifier not in bindings:
                    bindings[parameter.identifier] = []
                bindings[parameter.identifier].append(binding)

        parameter_tuple = tuple(parameters)

        binding_map = {parameter_id: tuple(parameter_bindings) for parameter_id, parameter_bindings in bindings.items()}

        definition = cls(
            identifier=cls._make_identifier(metadata.name),
            name=metadata.name,
            prototype=metadata.prototype,
            parameters=parameter_tuple,
            bindings=binding_map,
            description=metadata.description,
            version=metadata.version,
            asset_path=str(asset_path),
            metadata=metadata,
        )

        definition.validate()

        return definition

    @staticmethod
    def _make_identifier(name: str) -> str:
        """
        Convert the authored name into a stable identifier.

        This is intentionally conservative for now.
        """

        return name.strip().lower().replace(" ", "_").replace("-", "_")
