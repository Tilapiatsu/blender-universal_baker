from __future__ import annotations

from collections.abc import Callable, Iterator

from ..custom_bakers.definition import CustomBakerDefinition

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING


@dataclass(frozen=True)
class LazyDefinition:
    identifier: str
    asset_path: Path
    loader: Callable[[Path], CustomBakerDefinition]


class CustomBakerDefinitionError(RuntimeError):
    pass


class CustomBakerDefinitionNotFoundError(CustomBakerDefinitionError):
    pass


DefinitionLoader = Callable[[str], CustomBakerDefinition]


class CustomBakerDefinitionRegistry:
    def __init__(self, loader: DefinitionLoader | None = None) -> None:

        self._definitions: dict[str, CustomBakerDefinition] = {}
        self._loaders: dict[str, DefinitionLoader] = {}
        self._loader = loader
        self._lazy: dict[str, LazyDefinition] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, definition: CustomBakerDefinition) -> None:

        identifier = definition.identifier

        if identifier in self._definitions:
            raise CustomBakerDefinitionError(f"Definition '{identifier}' is already registered.")

        self._definitions[identifier] = definition

    def register_lazy(self, identifier: str, asset_path: Path, loader: Callable[[Path], CustomBakerDefinition]) -> None:
        self._lazy[identifier] = LazyDefinition(
            identifier=identifier,
            asset_path=asset_path,
            loader=loader,
        )

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, identifier: str) -> CustomBakerDefinition | None:
        definition = self._definitions.get(identifier)

        if definition is not None:
            return definition

        lazy = self._lazy.get(identifier)

        if lazy is None:
            return None

        definition = lazy.loader(lazy.asset_path)

        self._definitions[identifier] = definition

        del self._lazy[identifier]

        return definition

    def require(self, identifier: str) -> CustomBakerDefinition:
        definition = self.get(identifier)
        if definition is None:
            raise CustomBakerDefinitionNotFoundError(f"No definition registered for '{identifier}'.")

        return definition

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def is_loaded(self, identifier: str) -> bool:

        return identifier in self._definitions

    def is_registered(self, identifier: str) -> bool:

        return identifier in self._definitions or identifier in self._loaders

    def clear(self) -> None:
        self._definitions.clear()
        self._loaders.clear()
        self._lazy.clear()

    # ------------------------------------------------------------------
    # Iteration
    # ------------------------------------------------------------------

    def items(self):
        return self._definitions.items()

    def values(self):
        return self._definitions.values()

    def keys(self):
        return self._definitions.keys()

    def __getitem__(self, definition_id: str) -> CustomBakerDefinition:
        return self._definitions[definition_id]

    def __contains__(self, identifier: str) -> bool:

        return self.is_registered(identifier)

    def __len__(self) -> int:

        return len(self._definitions) + len(self._loaders)

    def __iter__(
        self,
    ) -> Iterator[CustomBakerDefinition]:

        return iter(self._definitions.values())


registry_definition = CustomBakerDefinitionRegistry()
