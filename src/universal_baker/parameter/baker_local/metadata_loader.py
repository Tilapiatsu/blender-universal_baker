from __future__ import annotations

from ..metadata import LocalBakerMetadata

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...bakers.base import BakerBase


class MetadataLoader:
    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @classmethod
    def load(cls, baker: BakerBase) -> LocalBakerMetadata:

        return LocalBakerMetadata(
            id=baker.id,
            name=baker.name,
            description=baker.description,
            parameters=baker.parameters,
        )
