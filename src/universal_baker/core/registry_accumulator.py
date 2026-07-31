from __future__ import annotations

from typing import Dict

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..accumulators.base import AccumulatorBase


class AccumulatorRegistry:
    def __init__(self):
        self._accumulator: Dict[str, AccumulatorBase] = {}

    def register(self, accumulator: AccumulatorBase) -> None:
        if accumulator.id in self._accumulator:
            raise ValueError(f"Accumulator '{accumulator.id}' already registered.")

        self._accumulator[accumulator.id] = accumulator

    def unregister(self, accumulator_id: str) -> None:
        self._accumulator.pop(accumulator_id, None)

    def __getitem__(self, accumulator_id: str) -> AccumulatorBase:
        return self._accumulator[accumulator_id]

    def exists(self, accumulator_id: str) -> bool:
        return accumulator_id in self._accumulator

    def items(self):
        return self._accumulator.items()

    def values(self):
        return self._accumulator.values()

    def keys(self):
        return self._accumulator.keys()

    def enum_items(self):
        items = []

        for accumulator in self._accumulator.values():
            items.append(
                (
                    accumulator.id,
                    accumulator.name,
                    accumulator.description,
                    accumulator.icon,
                    len(items),
                )
            )

        return items


registry_accumulator = AccumulatorRegistry()
