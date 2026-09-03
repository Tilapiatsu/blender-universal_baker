from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from ..parameter.baker_custom.definition import CustomBakerDefinition
from ..parameter.baker_local.definition import LocalBakerDefinition

if TYPE_CHECKING:
    from ..bakers.base import BakerBase


@dataclass(frozen=True)
class LazyCustomDefinition:
    identifier: str
    asset_path: Path
    loader: Callable[[Path], CustomBakerDefinition]


@dataclass(frozen=True)
class LazyLocalDefinition:
    identifier: str
    baker: BakerBase
    loader: Callable[[BakerBase], LocalBakerDefinition]


class BakerDefinitionError(RuntimeError):
    pass


class BakerDefinitionNotFoundError(BakerDefinitionError):
    pass


LocalDefinitionLoader = Callable[[str], LocalBakerDefinition]
CustomDefinitionLoader = Callable[[str], CustomBakerDefinition]


class BakerDefinitionRegistry:
    def __init__(self) -> None:
        self._local_definitions: dict[str, LocalBakerDefinition] = {}
        self._custom_definitions: dict[str, CustomBakerDefinition] = {}
        self._loaders_local: dict[str, LocalDefinitionLoader] = {}
        self._loaders_custom: dict[str, CustomDefinitionLoader] = {}
        self._lazy_local: dict[str, LazyLocalDefinition] = {}
        self._lazy_custom: dict[str, LazyCustomDefinition] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_local(self, definition: LocalBakerDefinition) -> None:
        identifier = definition.identifier
        if identifier in self._local_definitions:
            raise BakerDefinitionError(f"Definition '{identifier}' is already registered.")

        self._local_definitions[identifier] = definition

    def register_local_lazy(
        self, identifier: str, baker: BakerBase, loader: Callable[[BakerBase], LocalBakerDefinition]
    ) -> None:
        self._lazy_local[identifier] = LazyLocalDefinition(
            identifier=identifier,
            baker=baker,
            loader=loader,
        )

    def register_custom(self, definition: CustomBakerDefinition) -> None:

        identifier = definition.identifier

        if identifier in self._custom_definitions:
            raise BakerDefinitionError(f"Definition '{identifier}' is already registered.")

        self._custom_definitions[identifier] = definition

    def register_custom_lazy(
        self, identifier: str, asset_path: Path, loader: Callable[[Path], CustomBakerDefinition]
    ) -> None:
        self._lazy_custom[identifier] = LazyCustomDefinition(
            identifier=identifier,
            asset_path=asset_path,
            loader=loader,
        )

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, identifier: str) -> LocalBakerDefinition | CustomBakerDefinition | None:

        local = self.get_local(identifier)

        if local is not None:
            return local

        return self.get_custom(identifier)

    def get_local(self, identifier: str) -> LocalBakerDefinition | None:
        definition = self._local_definitions.get(identifier)

        if definition is not None:
            return definition

        lazy = self._lazy_local.get(identifier)

        if lazy is None:
            return None

        definition = lazy.loader(lazy.baker)

        self._local_definitions[identifier] = definition

        del self._lazy_local[identifier]

        return definition

    def require_local(self, identifier: str) -> LocalBakerDefinition:
        definition = self.get_local(identifier)
        if definition is None:
            raise BakerDefinitionNotFoundError(f"No definition registered for '{identifier}'.")

        return definition

    def get_custom(self, identifier: str) -> CustomBakerDefinition | None:
        definition = self._custom_definitions.get(identifier)

        if definition is not None:
            return definition

        lazy = self._lazy_custom.get(identifier)

        if lazy is None:
            return None

        definition = lazy.loader(lazy.asset_path)

        self._custom_definitions[identifier] = definition

        del self._lazy_custom[identifier]

        return definition

    def require_custom(self, identifier: str) -> CustomBakerDefinition:
        definition = self.get_custom(identifier)
        if definition is None:
            raise BakerDefinitionNotFoundError(f"No definition registered for '{identifier}'.")

        return definition

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def is_loaded(self, identifier: str) -> bool:
        return identifier in self._custom_definitions or identifier in self._local_definitions

    def is_registered(self, identifier: str) -> bool:
        return (
            identifier in self._custom_definitions
            or identifier in self._loaders_custom
            or identifier in self._local_definitions
        )

    def clear(self) -> None:
        self._custom_definitions.clear()
        self._local_definitions.clear()
        self._loaders_local.clear()
        self._loaders_custom.clear()
        self._lazy_custom.clear()

    # ------------------------------------------------------------------
    # Iteration
    # ------------------------------------------------------------------

    def custom_items(self):
        return self._custom_definitions.items()

    def custom_values(self):
        return self._custom_definitions.values()

    def custom_keys(self):
        return self._custom_definitions.keys()

    def local_items(self):
        return self._local_definitions.items()

    def local_values(self):
        return self._local_definitions.values()

    def local_keys(self):
        return self._local_definitions.keys()


registry_definition = BakerDefinitionRegistry()
