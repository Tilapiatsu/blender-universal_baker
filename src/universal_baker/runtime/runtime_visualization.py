from __future__ import annotations

import bpy

from contextlib import contextmanager

from ..constant import LOG
from ..enum.visualization import VisualizationMode
from .image_handle import ImageHandle
from ..core.registry_definition import registry_definition
from ..custom_bakers.parameter_applier import ParameterApplier
from ..parameter.parameter_context import ParameterContext

from typing import TYPE_CHECKING

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
        self._baker_group_uuid: str | None = None
        self._producer_uuid: str | None = None
        self._preview_enabled: bool = False
        self._preview_dirty: bool = False
        self._updating_parameters: bool = False
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
    def bake_group_uuid(self):
        return self._baker_group_uuid

    @property
    def producer_uuid(self):
        return self._producer_uuid

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
    def preview_enabled(self) -> bool:
        return self._preview_enabled

    # ------------------------------------------------------------------
    # Activation
    # ------------------------------------------------------------------

    def begin(
        self,
        mode: VisualizationMode,
        producer: BakerBase | PackerBase | None = None,
        image_handle: ImageHandle | None = None,
        bake_group_uuid: str | None = None,
        producer_uuid: str | None = None,
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
        self._baker_group_uuid = bake_group_uuid
        self._producer_uuid = producer_uuid
        self._preview_enabled = mode == VisualizationMode.PREVIEW

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

    def set_mode(self, mode: VisualizationMode) -> None:
        """
        Change visualization mode.

        This does not modify Blender itself. The visualization
        service is responsible for applying the new mode.
        """

        if not self._active:
            raise RuntimeError("Cannot change visualization mode while visualization is inactive")

        self._mode = mode

        self._preview_enabled = mode == VisualizationMode.PREVIEW

    def disable(self) -> None:
        from ..services.bake_visualization import BakeVisualizationService

        BakeVisualizationService.disable()

        self._preview_enabled = False

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

    def request_preview_refresh(self):
        self._preview_dirty = True

    def refresh_preview_parameters(self):
        if not self.preview_enabled:
            return

        if not self._preview_dirty:
            return

        if self._updating_parameters:
            return

        try:
            self._updating_parameters = True
            LOG.debug("Refreshing preview parameters")
            producer = self.active_producer

            if producer is None:
                LOG.error("Producer not defined")
                return

            definition = registry_definition.get(producer.id)

            if definition is None or self.producer_uuid is None:
                LOG.error(f"Definition not found for {producer.id}")
                return

            from ..core.controller import BakeController

            custom_baker = BakeController.get_baker_from_uuid(self.producer_uuid)

            if custom_baker is None:
                LOG.error("Custom Baker not Found")
                return

            from ..services.parameter_service import ParameterService

            snapshot = ParameterService.snapshot(definition, custom_baker)

            for o in bpy.context.scene.objects:
                materials = o.data.materials
                context = ParameterContext(object=o, materials=materials)

                ParameterApplier.apply(definition, snapshot, context)
        finally:
            self._updating_parameters = False
            self._preview_dirty = False

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
        self.active_producer: BakerBase | PackerBase | None = None
        self.bake_group_uuid: str | None = None
        self.producer_uuid: str | None = None

    def capture(self):
        self.was_enabled = self.runtime._active
        self.mode = self.runtime.mode
        self.active_producer = self.runtime.active_producer
        self.bake_group_uuid = self.runtime.bake_group_uuid
        self.producer_uuid = self.runtime.producer_uuid

    def restore(self):
        if not self.was_enabled or self.mode is None:
            return

        LOG.debug("Restore Visualization")
        from ..services.bake_visualization import BakeVisualizationService

        match self.mode:
            case VisualizationMode.DISPLAY:
                if self.bake_group_uuid is None or self.producer_uuid is None:
                    return
                BakeVisualizationService.enable_display(self.bake_group_uuid, self.producer_uuid)
            case VisualizationMode.PREVIEW:
                if self.active_producer is None or self.bake_group_uuid is None:
                    return
                BakeVisualizationService.enable_preview(self.active_producer, self.bake_group_uuid)
