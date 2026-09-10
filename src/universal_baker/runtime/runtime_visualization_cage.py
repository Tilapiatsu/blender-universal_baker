from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

import bpy

from ..constant import LOG
from ..parameter.parameter import BakerParameterType
from ..parameter.parameter_applier import ParameterApplier
from ..properties.baker_parameter import UBK_BakerParameterValue

if TYPE_CHECKING:
    from ..services.material_override import MaterialSnapshot
    from .visualization_state import SceneVisualizationState


class CageVisualizationRuntime:
    """
    Owns the transient runtime state of Universal Baker's
    viewport bake visualization system.

    This class deliberately does NOT contain persistent
    user configuration. Persistent settings live in
    properties.visualization.

    The runtime state exists only while Blender is running.
    """

    def __init__(self):
        self._active: bool = False
        self._baker_group_uuid: str | None = None
        self._target_uuid: str | None = None
        self._display_enabled: bool = False
        self._updating_parameters: bool = False
        self._cage_object: str | None = None
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
    def bake_group_uuid(self) -> str | None:
        return self._baker_group_uuid

    @property
    def target_uuid(self) -> str | None:
        return self._target_uuid

    @property
    def cage_object(self) -> bpy.types.Object:
        return bpy.data.objects.get(self._cage_object)

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

    @property
    def display_enabled(self) -> bool:
        return self._display_enabled

    # ------------------------------------------------------------------
    # Activation
    # ------------------------------------------------------------------

    def begin(
        self,
        bake_group_uuid: str | None = None,
        target_uuid: str | None = None,
        cage_object: str | None = None,
    ) -> None:
        """
        Start a new visualization session.

        The actual Blender state should already have been captured
        by the visualization service before calling this method.
        """

        if self._active:
            raise RuntimeError("Visualization runtime is already active")

        self._active = True
        self._baker_group_uuid = bake_group_uuid
        self._target_uuid = target_uuid
        self._cage_object = cage_object if cage_object is not None else ""

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

    def disable(self) -> None:
        from ..services.bake_visualization import BakeVisualizationService

        BakeVisualizationService.disable()

        self._display_enabled = False

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

        self._scenes.clear()
        self._material_snapshots.clear()
        self._cage_object = ""

    @contextmanager
    def suspend(self):
        suspension = VisualizationSuspension(self)

        suspension.capture()

        try:
            if suspension.was_enabled:
                LOG.debug("Suspend Visualization")
                self.disable()

            yield

        finally:
            suspension.restore()

    def do_suspend(self) -> VisualizationSuspension:
        suspension = VisualizationSuspension(self)

        suspension.capture()

        if suspension.was_enabled:
            LOG.debug("Suspend Visualization")
            self.disable()

        return suspension

    def request_preview_refresh(self):
        self._preview_dirty = True

    def clamp_ui_prop(
        self,
        ui_prop: UBK_BakerParameterValue,
        parameter_type: BakerParameterType,
        min: float,
        max: float,
    ):
        match parameter_type:
            case BakerParameterType.FLOAT:
                ui_prop.float_value = ParameterApplier.clamp_value(
                    ui_prop.float_value,
                    min,
                    max,
                )
            case BakerParameterType.INT:
                ui_prop.int_value = ParameterApplier.clamp_value(
                    ui_prop.int_value,
                    min,
                    max,
                )

    # ------------------------------------------------------------------
    # Debugging
    # ------------------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"active={self._active!r}, "
            f"scenes={len(self._scenes)}, "
            f"material_snapshots="
            f"{len(self._material_snapshots)}"
            f")"
        )


class VisualizationSuspension:
    def __init__(
        self,
        runtime: CageVisualizationRuntime,
    ):
        self.runtime = runtime
        self.was_enabled = False
        self.bake_group_uuid: str | None = None
        self.target_uuid: str | None = None
        self.cage_object: str | None = None

    def capture(self):
        self.was_enabled = self.runtime._active
        self.bake_group_uuid = self.runtime.bake_group_uuid
        self.target_uuid = self.runtime.target_uuid
        self.cage_object = self.runtime.cage_object

    def restore(self):
        if not self.was_enabled:
            return

        LOG.debug("Restore Visualization")
        from ..services.cage_visualization import CageVisualizationService

        # TODO: Need to properly enable_display
        CageVisualizationService.enable_display(data)
