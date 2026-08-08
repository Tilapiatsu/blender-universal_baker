from __future__ import annotations

from dataclasses import dataclass

from ..constant import LOG
from .output_base import OutputBase
from .bake_group import BakeGroup
from .output_artifact import OutputArtifact
from .tile_set import TileSet

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..packers.base import PackerBase
    from ..enum.channels import Channel
    from ..bakers.base import BakerBase


LOG_SCOPE: str = "Output Pack"


@dataclass(slots=True)
class OutputPack(OutputBase):
    r"""
    Runtime representation of a Pack image.

    A Pack Image can be composed from multiple bakers and 

    Example
    -------
    BakeTarget : Character

        R: AO  ------------ \
        G: METALIC  -------- \ ______ 1 Pack Image
        B: ROUGHNESS ------- /
        A: OPACITY  ------- /

    """

    packer: PackerBase

    red_baker: BakerBase | None
    green_baker: BakerBase | None
    blue_baker: BakerBase | None
    alpha_baker: BakerBase | None

    red_channel_mapping: Channel
    green_channel_mapping: Channel
    blue_channel_mapping: Channel
    alpha_channel_mapping: Channel

    @classmethod
    def create(
        cls,
        uuid: str,
        name: str,
        tiles: TileSet,
        bake_group: BakeGroup,
        packer: PackerBase,
        red_baker: BakerBase,
        green_baker: BakerBase,
        blue_baker: BakerBase,
        alpha_baker: BakerBase,
        red_channel_mapping: Channel,
        green_channel_mapping: Channel,
        blue_channel_mapping: Channel,
        alpha_channel_mapping: Channel,
    ) -> OutputPack:
        return cls(
            uuid=uuid,
            name=name,
            tiles=tiles,
            bake_group=bake_group,
            packer=packer,
            red_baker=red_baker,
            green_baker=green_baker,
            blue_baker=blue_baker,
            alpha_baker=alpha_baker,
            red_channel_mapping=red_channel_mapping,
            green_channel_mapping=green_channel_mapping,
            blue_channel_mapping=blue_channel_mapping,
            alpha_channel_mapping=alpha_channel_mapping,
        )

    @classmethod
    def from_artifact(cls, artifact: OutputArtifact) -> OutputPack:
        with LOG.scope(LOG_SCOPE):
            LOG.debug(f"Creating Pack Output : {artifact.data.filename}")
            from ..core.controller import BakeController

            image = artifact.load_image()
            tiles = TileSet.from_blender_image(image.image)

            packer = BakeController.get_paker_from_uuid(artifact.producer_uuid)
            red_baker = BakeController.get_baker_from_uuid(artifact.dependencies[0])
            green_baker = BakeController.get_baker_from_uuid(artifact.dependencies[1])
            blue_baker = BakeController.get_baker_from_uuid(artifact.dependencies[2])
            alpha_baker = BakeController.get_baker_from_uuid(artifact.dependencies[3])

            output = OutputPack(
                uuid=artifact.uuid,
                name=artifact.name,
                tiles=tiles,
                bake_group=BakeGroup(artifact.bake_group_uuid),
                packer=packer,
                red_baker=red_baker,
                green_baker=green_baker,
                blue_baker=blue_baker,
                alpha_baker=alpha_baker,
                red_channel_mapping=artifact.dependency_mapping[0],
                green_channel_mapping=artifact.dependency_mapping[1],
                blue_channel_mapping=artifact.dependency_mapping[2],
                alpha_channel_mapping=artifact.dependency_mapping[3],
            )

            return output

    def __repr__(self) -> str:
        return f"Pack Output : {self.name} {self.bake_group.name} | R: {self.red_baker.id if self.red_baker else 'NONE'} | G: {self.green_baker.id if self.green_baker else 'NONE'} | B: {self.blue_baker.id if self.blue_baker else 'NONE'} | A: {self.alpha_baker.id if self.alpha_baker else 'NONE'}"
