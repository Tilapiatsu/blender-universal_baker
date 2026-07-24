from __future__ import annotations

from typing import Dict

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..compositors.compositor import Compositor


class CompositorRegistry:
    def __init__(self):
        self._compositors: Dict[str, Compositor] = {}

    def register(self, compositor: Compositor) -> None:
        if compositor.id in self._compositors:
            raise ValueError(f"Compositor '{compositor.id}' already registered.")

        self._compositors[compositor.id] = compositor

    def unregister(self, compositor_id: str) -> None:
        self._compositors.pop(compositor_id, None)

    def __getitem__(self, compositor_id: str) -> Compositor:
        return self._compositors[compositor_id]

    def exists(self, compositor_id: str) -> bool:
        return compositor_id in self._compositors

    def items(self):
        return self._compositors.items()

    def values(self):
        return self._compositors.values()

    def keys(self):
        return self._compositors.keys()

    def enum_items(self):
        items = []

        for compositor in self._compositors.values():
            items.append(
                (
                    compositor.id,
                    compositor.name,
                    compositor.description,
                    compositor.icon,
                    len(items),
                )
            )

        return items


registry_compositor = CompositorRegistry()
