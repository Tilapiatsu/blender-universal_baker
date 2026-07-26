from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4

from .output_base import OutputBase
from .bake_group import BakeGroup

if TYPE_CHECKING:
    from bpy.types import Object

    from .image_buffer import ImageBuffer
    from ..bakers.base import BakerBase


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

    target_object: Object
    baker: BakerBase

    @classmethod
    def create(
        cls,
        bake_group: BakeGroup,
        target_object: Object,
        baker: BakerBase,
        image: ImageBuffer,
    ) -> OutputBake:
        return cls(
            uuid=str(uuid4()),
            image=image,
            bake_group=bake_group,
            target_object=target_object,
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

    @property
    def target_object_name(self) -> str:
        return self.target_object.name
