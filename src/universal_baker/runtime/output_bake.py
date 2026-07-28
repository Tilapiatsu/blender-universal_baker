from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4

from ..constant import LOG
from .output_base import OutputBase
from .bake_group import BakeGroup
from .output_artifact import OutputArtifact
from ..services.image_io import ImageIOService

if TYPE_CHECKING:
    from .image_buffer import ImageBuffer
    from ..bakers.base import BakerBase

LOG_SCOPE: str = "Output Bake"


@dataclass(slots=True)
class OutputBake(OutputBase):
    """
    Runtime representation of a baked image.

    One BakeTask always produces one OutputBake.

    Example
    -------
    BakeTarget : Character

        Head  ----\
        Body  -----+---- AO ----> 3 OutputBakes
        Teeth ----/

    They can later be accumulated into one image.
    """

    baker: BakerBase

    @classmethod
    def create(
        cls,
        uuid: str,
        bake_group: BakeGroup,
        baker: BakerBase,
        image: ImageBuffer,
    ) -> OutputBake:
        return cls(
            uuid=uuid,
            image=image,
            bake_group=bake_group,
            baker=baker,
        )

    @property
    def baker_id(self) -> str:
        return self.baker.id

    @property
    def baker_name(self) -> str:
        return self.baker.name

    @property
    def bake_group_name(self) -> str:
        return self.bake_group.name

    @classmethod
    def from_artifact(cls, artifact: OutputArtifact) -> OutputBake:
        with LOG.scope(LOG_SCOPE):
            LOG.debug(f"Creating Output : {artifact.data.filename}")

            from ..core.controller import BakeController

            image = artifact.load_image()
            image_buffer = ImageIOService.read(image)

            baker = BakeController.get_baker_from_uuid(artifact.producer_uuid)

            output = OutputBake(
                uuid=artifact.uuid,
                bake_group=BakeGroup(artifact.bake_group_uuid),
                baker=baker,
                image=image_buffer,
            )

            return output

    def __repr__(self) -> str:
        return f"Bake Output : {self.bake_group.name} | {self.baker.name}"
