from __future__ import annotations

from typing import TYPE_CHECKING

from ..baker_local.definition import LocalBakerDefinition
from ..metadata import LocalBakerMetadata

if TYPE_CHECKING:
    from ...bakers.base import BakerBase


class MetadataLoader:
    @classmethod
    def load(cls, baker: BakerBase) -> LocalBakerMetadata:

        return LocalBakerMetadata(
            id=baker.id,
            name=baker.name,
            description=baker.description,
            parameters=baker.parameters,
        )

    @classmethod
    def load_definition(cls, baker: BakerBase) -> LocalBakerDefinition:
        metadata = cls.load(baker)

        return LocalBakerDefinition.from_metadata(metadata)
