from __future__ import annotations

from ..core.registry_definition import registry_definition
from ..parameter.baker_local.metadata_loader import MetadataLoader as metadata_loader_local
from ..parameter.metadata import BindingMetadata, ParameterMetadata
from ..services.cage_object import CageObjectService


class DefinitionCage:
    id: str = "CAGE"
    name: str = "Cage"
    description: str = "Defines the Cage Parameters"

    @property
    def parameters(self) -> tuple[ParameterMetadata, ...]:
        parameters: tuple[ParameterMetadata, ...] = ()

        b: tuple[BindingMetadata, ...] = (
            BindingMetadata(
                binding_type="MODIFIER_PROPERTY",
                modifier=CageObjectService.MODIFIER_NAME,
                property="strength",
            ),
        )
        p = ParameterMetadata(
            identifier="cage_extrusion",
            name="Cage Extrude",
            default=0.1,
            description="The max displacement for the cage",
            type="FLOAT",
            category="Cage",
            order=0,
            visible=True,
            bindings=b,
        )

        parameters += (p,)

        return parameters


def register():
    registry_definition.register_local_lazy(
        identifier="CAGE",
        definition_object=DefinitionCage(),
        loader=metadata_loader_local.load_definition,
    )


def unregister(): ...
