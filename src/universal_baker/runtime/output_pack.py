from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4

from ..packers.packer_base import PackerBase
from .image_buffer import ImageBuffer

from .output_base import OutputBase
from .bake_group import BakeGroup

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
