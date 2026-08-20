from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import bpy

if TYPE_CHECKING:
    from ..bakers.base import BakerBase
    from ..services.material_override import MaterialSnapshot


@dataclass
class ViewportState:
    """
    Snapshot of a single 3D viewport.

    This is runtime-only and must never be stored in a
    Blender PropertyGroup.
    """

    area: bpy.types.Area

    shading_type: str
    color_type: str


@dataclass
class SceneVisualizationState:
    """
    Runtime snapshot of the Blender state belonging to a scene.
    """

    render_engine: str | None = None

    viewports: list[ViewportState] = field(
        default_factory=list,
    )


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

        self._mode: str | None = None

        self._active_producer = None

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
    def mode(self) -> str | None:
        """
        Current visualization mode.

        Expected values:

            None
            "PREVIEW"
            "DISPLAY"
        """
        return self._mode

    @property
    def active_baker(self):
        """
        Baker currently being visualized.
        """
        return self._active_producer

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
        mode: str,
        producer=None,
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
    # Baker
    # ------------------------------------------------------------------

    def set_active_producer(
        self,
        producer,
    ) -> None:
        """
        Change the baker currently being visualized.
        """

        self._active_producer = producer

    # ------------------------------------------------------------------
    # Mode
    # ------------------------------------------------------------------

    def set_mode(
        self,
        mode: str,
    ) -> None:
        """
        Change visualization mode.

        This does not modify Blender itself. The visualization
        service is responsible for applying the new mode.
        """

        if not self._active:
            raise RuntimeError("Cannot change visualization mode while visualization is inactive")

        self._mode = mode

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

        self._scenes.clear()
        self._material_snapshots.clear()

    # ------------------------------------------------------------------
    # Debugging
    # ------------------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"active={self._active!r}, "
            f"mode={self._mode!r}, "
            f"active_baker={self._active_producer!r}, "
            f"scenes={len(self._scenes)}, "
            f"material_snapshots="
            f"{len(self._material_snapshots)}"
            f")"
        )
