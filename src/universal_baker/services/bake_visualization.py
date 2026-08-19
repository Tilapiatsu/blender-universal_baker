from __future__ import annotations

import bpy

from ..constant import LOG

from ..runtime.visualization_state import (
    VisualizationState,
)

from .viewport import ViewportService
from .preview_material import PreviewMaterialService
from .material_display import DisplayMaterialService
from .material_override import MaterialOverrideService
from ..core.registry_baker import registry_baker
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bakers.base import BakerBase


def update_visualization(self, context):
    with LOG.scope("Visualization"):
        from ..core.controller import BakeController

        project = BakeController.project(context)

        viz = project.visualization

        if viz.refreshing:
            return

        if project is None:
            LOG.warning("Project not found")
            return

        bake_group = BakeController.active_bake_group(context)

        if bake_group is None:
            LOG.warning("Bake Group not found")
            return

        baker = BakeController.active_baker(context)

        if baker is None:
            LOG.warning("Baker not found")
            return

        if viz.baker_idx != bake_group.active_baker_index:
            viz.baker_idx = bake_group.active_baker_index
            producer = registry_baker[baker.baker]
            BakeVisualizationService.refresh(producer, bake_group.uuid, baker.accumulated_uuid)

        elif not viz.enabled_preview and not viz.enabled_display:
            viz.mode = "NONE"
            BakeVisualizationService.disable()
            return

        if viz.enabled_preview and viz.mode != "PREVIEW":
            LOG.debug("Enabling Preview")
            viz.refreshing = True
            viz.enabled_display = False
            viz.mode = "PREVIEW"
            producer = registry_baker[baker.baker]
            BakeVisualizationService.enable_preview(producer)
            viz.refreshing = False

        elif viz.enabled_display and viz.mode != "DISPLAY":
            LOG.debug("Enabling Display")
            viz.refreshing = True
            viz.enabled_preview = False
            viz.mode = "DISPLAY"
            BakeVisualizationService.enable_display(bake_group.uuid, baker.accumulated_uuid)
            viz.refreshing = False


class BakeVisualizationService:
    _state: VisualizationState | None = None

    # ---------------------------------------------------------
    # State
    # ---------------------------------------------------------

    @classmethod
    def is_active(cls) -> bool:
        return cls._state is not None and cls._state.active

    @classmethod
    def mode(cls) -> str | None:

        if cls._state is None:
            return None

        return cls._state.mode

    # ---------------------------------------------------------
    # Preview
    # ---------------------------------------------------------

    @classmethod
    def enable_preview(
        cls,
        baker: BakerBase,
    ):

        if cls.is_active():
            cls.disable()

        cls._state = ViewportService.capture_state()

        cls._state.active = True
        cls._state.mode = "PREVIEW"

        material = PreviewMaterialService.get_or_create()

        # Baker-specific hook.
        baker.configure_preview_material(material)

        cls._state.material_snapshots = MaterialOverrideService.apply(material)

        # Cycles
        for scene in bpy.data.scenes:
            scene.render.engine = "CYCLES"

        ViewportService.set_rendered()

    # ---------------------------------------------------------
    # Display
    # ---------------------------------------------------------

    @staticmethod
    def _get_image(bake_group_uuid: str, baker_uuid: str) -> bpy.types.Image | None:
        from ..runtime.runtime_manager import RuntimeManager

        runtime = RuntimeManager.current(bpy.context)

        handles = runtime.provider.get_producer_image(bake_group_uuid=bake_group_uuid, producer_uuid=baker_uuid)

        if handles is None:
            return

        if len(handles) > 1:
            LOG.warning(f"{len(handles)} handles found.")

        image = handles[0].image()

        return image

    @classmethod
    def enable_display(
        cls,
        bake_group_uuid: str,
        baker_uuid: str,
    ):

        # ISSUE: All materials turns to pink if baking wile in diplay mode
        if cls.is_active():
            cls.disable()

        cls._state = ViewportService.capture_state()

        cls._state.active = True
        cls._state.mode = "DISPLAY"

        material = DisplayMaterialService.get_or_create()

        image = cls._get_image(bake_group_uuid, baker_uuid)

        if image is None:
            return

        DisplayMaterialService.set_image(
            material,
            image.image,
        )

        cls._state.material_snapshots = MaterialOverrideService.apply(material)

        ViewportService.set_texture()

    # ---------------------------------------------------------
    # Disable
    # ---------------------------------------------------------

    @classmethod
    def disable(cls):

        state = cls._state

        if state is None:
            return

        MaterialOverrideService.restore(state.material_snapshots)

        ViewportService.restore(state)

        cls._state = None

    # ---------------------------------------------------------
    # Refresh
    # ---------------------------------------------------------

    @classmethod
    def refresh(
        cls,
        baker: BakerBase | None = None,
        bake_group_uuid: str | None = None,
        baker_uuid: str | None = None,
    ):

        if not cls.is_active():
            return

        mode = cls.mode()

        if mode == "PREVIEW":
            if baker is None:
                return

            cls.disable()

            cls.enable_preview(baker)

        elif mode == "DISPLAY":
            if bake_group_uuid is None or baker_uuid is None:
                return

            cls.disable()

            cls.enable_display(bake_group_uuid, baker_uuid)
