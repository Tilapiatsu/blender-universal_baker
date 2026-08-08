from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..constant import LOG
from .output_base import OutputBase
from .output_bake import OutputBake
from .bake_group import BakeGroup
from .output_artifact import OutputArtifact
from .tile_set import TileSet

if TYPE_CHECKING:
    from ..bakers.base import BakerBase

LOG_SCOPE: str = "Output Accumulated"


@dataclass(slots=True)
class OutputAccumulated(OutputBase):
    """
    Runtime representation of a Accumulated image ( computed from multiple bakes ).

    One BakeTask always produces one OutputBake.

    One bake group can create multiple OutputBakes that get accumulated into one image.

    Example
    -------
    BakeTarget : Character

        Head  ----\
        Body  -----+---- AO ----> 3 OutputBakes  ----> 1 OutputAccumulated
        Teeth ----/

    """

    output_bakes: list[OutputBake]
    baker: BakerBase

    @classmethod
    def create(
        cls,
        uuid: str,
        name: str,
        bake_group: BakeGroup,
        output_bakes: list[OutputBake],
        baker: BakerBase,
        tiles: TileSet,
    ) -> OutputAccumulated:
        return cls(
            uuid=uuid,
            name=name,
            tiles=tiles,
            bake_group=bake_group,
            output_bakes=output_bakes,
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
    def from_artifact(cls, artifact: OutputArtifact) -> OutputAccumulated:
        with LOG.scope(LOG_SCOPE):
            LOG.debug(f"Creating Accumulated Output : {artifact.name}")
            from ..core.controller import BakeController

            image = artifact.load_image()
            tiles = TileSet.from_blender_image(image.image)

            output_bakes = []
            for d in artifact.dependencies:
                baker = BakeController.get_baker_from_uuid(d)
                if baker is None:
                    continue

                output_bakes.append(baker)

            baker = BakeController.get_baker_from_uuid(artifact.producer_uuid)

            output = OutputAccumulated(
                uuid=artifact.uuid,
                name=artifact.name,
                tiles=tiles,
                baker=baker,
                bake_group=BakeGroup(artifact.bake_group_uuid),
                output_bakes=output_bakes,
            )

            return output

    def __repr__(self) -> str:
        return f"Accumulated Output : {self.bake_group.name} | {self.baker.id}"
