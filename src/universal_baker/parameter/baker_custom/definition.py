from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..binding import ParameterBinding
from ..binding_factory import BindingFactory
from ..definition_base import DefinitionBase, DefinitionError
from ..metadata import CustomBakerMetadata
from ..parameter import Parameter
from ..parameter_factory import ParameterFactory


@dataclass(frozen=True)
class CustomBakerDefinition(DefinitionBase):
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
    prototype: str = ""
    bake_colorspace: str = ""
    image_colorspace: str = ""

    display_device: str = ""
    view_transform: str = ""
    look: str = ""

    exposure: float = 0.0
    gamma: float = 1.0

    parameters: tuple[Parameter, ...] = ()
    bindings: dict[str, tuple[ParameterBinding, ...]] = field(default_factory=dict)
    description: str = ""
    version: int = 1
    asset_path: str | None = None
    metadata: CustomBakerMetadata | None = None

    def _validate_identity(self) -> None:
        super()._validate_identity()

        if not self.prototype:
            raise DefinitionError(f"Custom Baker '{self.name}' does not define a prototype.")

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
            prototype=metadata.prototype,
            bake_colorspace=metadata.bake_colorspace,
            image_colorspace=metadata.image_colorspace,
            display_device=metadata.display_device,
            view_transform=metadata.view_transform,
            look=metadata.look,
            exposure=metadata.exposure,
            gamma=metadata.gamma,
            parameters=parameter_tuple,
            bindings=binding_map,
            description=metadata.description,
            version=metadata.version,
            asset_path=str(asset_path),
            metadata=metadata,
        )

        definition.validate()

        return definition
