from __future__ import annotations

from typing import Dict

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bakers.base import BaseBaker


class BakerRegistry:
    def __init__(self):
        self._bakers: Dict[str, BaseBaker] = {}

    def register(self, baker: BaseBaker) -> None:
        if baker.id in self._bakers:
            raise ValueError(f"Baker '{baker.id}' already registered.")

        self._bakers[baker.id] = baker

    def unregister(self, baker_id: str) -> None:
        self._bakers.pop(baker_id, None)

    def __getitem__(self, baker_id: str) -> BaseBaker:
        return self._bakers[baker_id]

    def exists(self, baker_id: str) -> bool:
        return baker_id in self._bakers

    def items(self):
        return self._bakers.items()

    def values(self):
        return self._bakers.values()

    def keys(self):
        return self._bakers.keys()

    def enum_items(self):
        items = []

        for baker in self._bakers.values():
            items.append(
                (
                    baker.id,
                    baker.label,
                    baker.description,
                    baker.icon,
                    len(items),
                )
            )

        return items


registry_baker = BakerRegistry()
