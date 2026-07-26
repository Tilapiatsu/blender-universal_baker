from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4

from .output_base import OutputBase
from .output_bake import OutputBake

if TYPE_CHECKING:
    from bpy.types import Object

    from .image_buffer import ImageBuffer
    from ..properties.bake_group import UBK_BakeGroup
    from ..bakers.base import BakerBase


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

    bake_group: UBK_BakeGroup
    target_objects: list[Object]
    output_bakes: list[OutputBake]
    baker: BakerBase

    @classmethod
    def create(
        cls,
        bake_group: UBK_BakeGroup,
        target_objects: list[Object],
        output_bakes: list[OutputBake],
        baker: BakerBase,
        image: ImageBuffer,
    ) -> OutputAccumulated:
        return cls(
            uuid=str(uuid4()),
            image=image,
            bake_group=bake_group,
            target_objects=target_objects,
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
