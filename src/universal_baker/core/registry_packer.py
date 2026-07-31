from __future__ import annotations

from typing import Dict

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..packers.base import PackerBase


class PackerRegistry:
    def __init__(self):
        self._packers: Dict[str, PackerBase] = {}

    def register(self, packer: PackerBase) -> None:
        if packer.id in self._packers:
            raise ValueError(f"Packer '{packer.id}' already registered.")

        self._packers[packer.id] = packer

    def unregister(self, packer_id: str) -> None:
        self._packers.pop(packer_id, None)

    def __getitem__(self, packer_id: str) -> PackerBase:
        return self._packers[packer_id]

    def exists(self, packer_id: str) -> bool:
        return packer_id in self._packers

    def items(self):
        return self._packers.items()

    def values(self):
        return self._packers.values()

    def keys(self):
        return self._packers.keys()

    def enum_items(self):
        items = []

        for packer in self._packers.values():
            items.append(
                (
                    packer.id,
                    packer.name,
                    packer.description,
                    packer.icon,
                    len(items),
                )
            )

        return items


registry_packer = PackerRegistry()
