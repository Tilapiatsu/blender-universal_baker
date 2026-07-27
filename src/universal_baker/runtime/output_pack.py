from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4

from ..packers.packer_base import PackerBase
from .image_buffer import ImageBuffer

from .output_base import OutputBase
from .bake_group import BakeGroup
from .output_artifact import OutputArtifact
from ..services.image_io import ImageIOService
from ..core.controller import BakeController

if TYPE_CHECKING:
    from ..packers.channels import Channel
    from ..bakers.base import BakerBase


@dataclass(slots=True)
class OutputPack(OutputBase):
    """
    Runtime representation of a Pack image.

    A Pack Image can be composed from multiple bakers and 

    Example
    -------
    BakeTarget : Character

        R: AO  ------------\
        G: METALIC  --------\ ______ 1 Pack Image
        B: ROUGHNESS -------/
        A: OPACITY  -------/

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
        image: ImageBuffer,
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
            uuid=str(uuid4()),
            image=image,
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
    def from_artifact(cls, artifact: OutputArtifact) -> OutputBake:
        image = artifact.load_image()
        image_buffer = ImageIOService.read(image)

        packer = BakeController.get_paker_from_uuid(artifact.producer_uuid)
        red_baker = BakeController.get_baker_from_uuid(artifact.dependencies[0])
        green_baker = BakeController.get_baker_from_uuid(artifact.dependencies[1])
        blue_baker = BakeController.get_baker_from_uuid(artifact.dependencies[2])
        alpha_baker = BakeController.get_baker_from_uuid(artifact.dependencies[3])

        output = OutputPack(
            uuid=artifact.uuid,
            image=image_buffer,
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
