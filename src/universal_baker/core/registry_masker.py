from __future__ import annotations

from typing import Dict

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..maskers.base import MaskerBase


class MaskerRegistry:
    def __init__(self):
        self._maskers: Dict[str, MaskerBase] = {}

    def register(self, masker: MaskerBase) -> None:
        if masker.id in self._maskers:
            raise ValueError(f"Masker '{masker.id}' already registered.")

        self._maskers[masker.id] = masker

    def unregister(self, masker_id: str) -> None:
        self._maskers.pop(masker_id, None)

    def __getitem__(self, masker_id: str) -> MaskerBase:
        return self._maskers[masker_id]

    def exists(self, masker_id: str) -> bool:
        return masker_id in self._maskers

    def items(self):
        return self._maskers.items()

    def values(self):
        return self._maskers.values()

    def keys(self):
        return self._maskers.keys()

    def enum_items(self):
        items = []

        for masker in self._maskers.values():
            items.append(
                (
                    masker.id,
                    masker.name,
                    masker.description,
                    masker.icon,
                    len(items),
                )
            )

        return items


registry_masker = MaskerRegistry()
