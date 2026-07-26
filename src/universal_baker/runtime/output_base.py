from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .bake_group import BakeGroup

if TYPE_CHECKING:
    from .image_buffer import ImageBuffer


@dataclass(slots=True)
class OutputBase:
    uuid: str
    image: ImageBuffer
    bake_group: BakeGroup
