from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import Iterator
from typing import TypeVar

T = TypeVar("T")


class PropertyCollectionService(ABC, Generic[T]):
    """Base class for services manipulating Blender CollectionProperties.

    Subclasses only have to implement:

        collection(owner)
        get_active_index(owner)
        set_active_index(owner, index)

    Everything else is generic.
    """

    # ------------------------------------------------------------------
    # Collection Access
    # ------------------------------------------------------------------

    @classmethod
    @abstractmethod
    def collection(cls, owner):
        """Return the Blender CollectionProperty."""

        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_active_index(cls, owner) -> int:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def set_active_index(cls, owner, index: int):
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @classmethod
    def count(cls, owner) -> int:
        return len(cls.collection(owner))

    @classmethod
    def empty(cls, owner) -> bool:
        return cls.count(owner) == 0

    @classmethod
    def valid_index(cls, owner, index: int) -> bool:
        return 0 <= index < cls.count(owner)

    # ------------------------------------------------------------------
    # Active
    # ------------------------------------------------------------------

    @classmethod
    def active(cls, owner) -> T | None:
        collection = cls.collection(owner)

        if not collection:
            return None

        index = cls.get_active_index(owner)

        if not cls.valid_index(owner, index):
            return None

        return collection[index]

    @classmethod
    def set_active(cls, owner, index: int):
        count = cls.count(owner)

        if count == 0:
            cls.set_active_index(owner, 0)

            return

        index = max(
            0,
            min(index, count - 1),
        )

        cls.set_active_index(owner, index)

    # ------------------------------------------------------------------
    # Collection Manipulation
    # ------------------------------------------------------------------

    @classmethod
    def remove(cls, owner, index: int):
        if not cls.valid_index(owner, index):
            return

        cls.collection(owner).remove(index)

        cls.set_active(
            owner,
            min(index, cls.count(owner) - 1),
        )

    @classmethod
    def clear(cls, owner):
        cls.collection(owner).clear()

        cls.set_active_index(owner, 0)

    # ------------------------------------------------------------------
    # Iteration
    # ------------------------------------------------------------------

    @classmethod
    def iter(cls, owner) -> Iterator[T]:
        yield from cls.collection(owner)

    @classmethod
    def enabled(cls, owner) -> Iterator[T]:
        for item in cls.collection(owner):
            if getattr(item, "enabled", True):
                yield item

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    @classmethod
    def first(cls, owner, predicate) -> T | None:
        for item in cls.collection(owner):
            if predicate(item):
                return item

        return None
