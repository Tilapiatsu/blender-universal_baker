from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, Protocol

from ..baker_local.definition import LocalDefinition
from ..metadata import LocalMetadata, ParameterMetadata


class DefinitionObject(Protocol):
    id: str
    name: str
    description: str

    @property
    @abstractmethod
    def parameters(self) -> tuple[ParameterMetadata, ...]: ...


class MetadataLoader:
    @classmethod
    def load(cls, definition_object: DefinitionObject) -> LocalMetadata:

        return LocalMetadata(
            id=definition_object.id,
            name=definition_object.name,
            description=definition_object.description,
            parameters=definition_object.parameters,
        )

    @classmethod
    def load_definition(cls, definition_object: DefinitionObject) -> LocalDefinition:
        metadata = cls.load(definition_object)

        return LocalDefinition.from_metadata(metadata)
