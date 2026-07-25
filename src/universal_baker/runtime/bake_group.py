from __future__ import annotations
from dataclasses import dataclass

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..core.controller import BakeController
    from ..properties.bake_group import UBK_BakeGroup


@dataclass(slots=True)
class BakeGroup:
    uuid: str
    name: str

    def get(self) -> UBK_BakeGroup | None:
        return BakeController.get_bake_group_from_uuid(self.uuid)
