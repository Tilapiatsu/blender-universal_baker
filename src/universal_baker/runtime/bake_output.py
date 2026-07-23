from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from bpy.types import Object

    from .image_buffer import ImageBuffer
    from ..properties.bake_group import UBK_BakeGroup
    from ..baker.base import BaseBaker


@dataclass(slots=True)
class BakeOutput:
    """
    Runtime representation of a baked image.

    One BakeTask always produces one BakeOutput.

    Example
    -------
    BakeTarget : Character

        Head  ----\
        Body  -----+---- AO ----> 3 BakeOutputs
        Teeth ----/

    They can later be accumulated into one image.
    """

    id: str
    bake_group: UBK_BakeGroup
    target_object: Object
    baker: BaseBaker
    image: ImageBuffer

    @classmethod
    def create(cls, *, bake_group, target_object, baker, image) -> "BakeOutput":
        return cls(
            id=str(uuid4()),
            bake_group=bake_group,
            target_object=target_object,
            baker=baker,
            image=image,
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

    @property
    def target_object_name(self) -> str:
        return self.target_object.name
