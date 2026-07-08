from __future__ import annotations

from enum import Enum, auto
from abc import ABC
from abc import abstractmethod

from ..baker.context import BakeContext
from ..baker.task import BakeTask


class BakerColorType(Enum):
    COLOR = auto()
    DATA = auto()
    MASK = auto()
    VECTOR = auto()


class BaseBaker(ABC):
    """Abstract baker interface.

    Every baker is responsible for preparing Blender,
    executing one bake, then restoring the scene.

    The executor knows nothing about AO, Curvature,
    Diffuse, etc.
    """

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    id: str = ""
    label: str = ""
    description: str = ""
    icon: str = "RENDER_STILL"
    color_type: BakerColorType = BakerColorType.COLOR

    # ------------------------------------------------------------------
    # Optional
    # ------------------------------------------------------------------

    def poll(self, task: BakeTask) -> bool:
        """Whether this baker can execute this task."""
        return True

    # ------------------------------------------------------------------
    # Mandatory
    # ------------------------------------------------------------------

    @abstractmethod
    def prepare(
        self,
        context: BakeContext,
        task: BakeTask,
    ) -> None:
        """Prepare Blender before baking."""

    @abstractmethod
    def bake(
        self,
        context: BakeContext,
        task: BakeTask,
    ) -> None:
        """Execute the bake."""

    @abstractmethod
    def cleanup(
        self,
        context: BakeContext,
        task: BakeTask,
    ) -> None:
        """Restore Blender."""
