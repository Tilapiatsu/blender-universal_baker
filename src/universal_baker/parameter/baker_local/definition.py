from __future__ import annotations

from dataclasses import dataclass, field

from ..binding import ParameterBinding
from ..binding_factory import BindingFactory
from ..definition_base import DefinitionBase
from ..metadata import LocalMetadata
from ..parameter import Parameter
from ..parameter_factory import ParameterFactory


@dataclass(frozen=True)
class LocalDefinition(DefinitionBase):
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
    metadata: LocalMetadata | None = None

    @classmethod
    def from_metadata(
        cls,
        metadata: LocalMetadata,
    ) -> LocalDefinition:
        """
        Build a Definition from the results of
        MetadataLoader, ParameterFactory and BindingFactory.
        """
        parameter_factory = ParameterFactory()
        binding_factory = BindingFactory()
        parameters: list[Parameter] = []
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
            parameters=parameter_tuple,
            bindings=binding_map,
            description=metadata.description,
            metadata=metadata,
        )

        definition.validate()

        return definition
