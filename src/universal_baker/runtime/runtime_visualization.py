from __future__ import annotations

from contextlib import contextmanager

from typing import TYPE_CHECKING

from ..enum.visualization import VisualizationMode
from .image_handle import ImageHandle


if TYPE_CHECKING:
    from ..services.material_override import MaterialSnapshot
    from .visualization_state import SceneVisualizationState
    from ..bakers.base import BakerBase
    from ..packers.base import PackerBase


class VisualizationRuntime:
    """
    Owns the transient runtime state of Universal Baker's
    viewport visualization system.

    This class deliberately does NOT contain persistent
    user configuration. Persistent settings live in
    properties.visualization.

    The runtime state exists only while Blender is running.
    """

    def __init__(self):
        self._active: bool = False
        self._mode: VisualizationMode | None = None
        self._active_producer = None
        self._active_image_handle = None
        self._scenes: dict[
            str,
            SceneVisualizationState,
        ] = {}

        self._material_snapshots: list[MaterialSnapshot] = []

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    @property
    def active(self) -> bool:
        """
        True when Universal Baker currently owns the
        visualization state.
        """
        return self._active

    @property
    def mode(self) -> VisualizationMode | None:
        """
        Current visualization mode.

        Expected values:
            None
            "PREVIEW"
            "DISPLAY"
        """
        return self._mode

    @property
    def active_producer(self):
        """
        Baker currently being visualized.
        """
        return self._active_producer

    @property
    def active_image_handle(self):
        """
        ImageHandle currently being visualized.
        """
        return self._active_image_handle

    @property
    def scenes(
        self,
    ) -> dict[str, SceneVisualizationState]:
        """
        Saved scene states.

        Exposed primarily to visualization services that need
        to restore Blender state.
        """
        return self._scenes

    @property
    def material_snapshots(self):
        """
        Saved material assignments.

        Exposed to MaterialOverrideService during restoration.
        """
        return self._material_snapshots

    # ------------------------------------------------------------------
    # Activation
    # ------------------------------------------------------------------

    def begin(
        self,
        mode: VisualizationMode,
        producer: BakerBase | PackerBase | None = None,
        image_handle: ImageHandle | None = None,
    ) -> None:
        """
        Start a new visualization session.

        The actual Blender state should already have been captured
        by the visualization service before calling this method.
        """

        if self._active:
            raise RuntimeError("Visualization runtime is already active")

        self._active = True
        self._mode = mode
        self._active_producer = producer
        self._active_image_handle = image_handle

    # ------------------------------------------------------------------
    # State registration
    # ------------------------------------------------------------------

    def set_scene_state(
        self,
        scene_name: str,
        state: SceneVisualizationState,
    ) -> None:
        """
        Store the original state of a Blender scene.
        """

        if not self._active:
            raise RuntimeError("Cannot store visualization state before visualization begins")

        self._scenes[scene_name] = state

    def set_material_snapshots(
        self,
        snapshots,
    ) -> None:
        """
        Store the original material assignments.
        """

        if not self._active:
            raise RuntimeError("Cannot store material state before visualization begins")

        self._material_snapshots = list(snapshots)

    # ------------------------------------------------------------------
    # Producer
    # ------------------------------------------------------------------

    def set_active_producer(
        self,
        producer: BakerBase | PackerBase | None,
    ) -> None:
        """
        Change the baker currently being visualized.
        """

        self._active_producer = producer

    # ------------------------------------------------------------------
    # Image Handle
    # ------------------------------------------------------------------

    def set_active_image_handle(
        self,
        image_handle: ImageHandle,
    ) -> None:
        """
        Change the baker currently being visualized.
        """

        self._active_image_handle = image_handle

    # ------------------------------------------------------------------
    # Mode
    # ------------------------------------------------------------------

    def set_mode(
        self,
        mode: VisualizationMode,
    ) -> None:
        """
        Change visualization mode.

        This does not modify Blender itself. The visualization
        service is responsible for applying the new mode.
        """

        if not self._active:
            raise RuntimeError("Cannot change visualization mode while visualization is inactive")

        self._mode = mode

    def disable(self) -> None:
        self.set_mode(VisualizationMode.NONE)

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """
        Clear all runtime visualization state.

        This does NOT restore Blender.

        Restoration is the responsibility of
        BakeVisualizationService.

        This distinction is important because the runtime should
        only own state, not the orchestration of restoring it.
        """

        self._active = False
        self._mode = None
        self._active_producer = None
        self._active_image_handle = None

        self._scenes.clear()
        self._material_snapshots.clear()

    @contextmanager
    def suspend(self):
        suspension = VisualizationSuspension(self)

        suspension.capture()

        try:
            if suspension.was_enabled:
                self.disable()

            yield

        finally:
            suspension.restore()

    # ------------------------------------------------------------------
    # Debugging
    # ------------------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"active={self._active!r}, "
            f"mode={self._mode!r}, "
            f"active_producer={self._active_producer!r}, "
            f"active_image_handle={self._active_image_handle!r}, "
            f"scenes={len(self._scenes)}, "
            f"material_snapshots="
            f"{len(self._material_snapshots)}"
            f")"
        )


class VisualizationSuspension:
    def __init__(
        self,
        runtime: VisualizationRuntime,
    ):
        self.runtime = runtime
        self.was_enabled = False
        self.mode = None
        self.active_producer = None
        self.active_image_handle = None

    def capture(self):
        self.was_enabled = self.runtime._active
        self.mode = self.runtime.mode
        self.active_producer = self.runtime.active_producer
        self.active_image_handle = self.runtime.active_image_handle

    def restore(self):
        if not self.was_enabled or self.mode is None or self.mode == VisualizationMode.NONE:
            return

        self.runtime.begin(
            mode=self.mode,
            producer=self.active_producer,
            image_handle=self.active_image_handle,
        )
