from __future__ import annotations

from dataclasses import dataclass

import bpy

from ..constant import LOG

from ..runtime.runtime_visualization import VisualizationRuntime

from ..enum.visualization import VisualizationMode
from .viewport import ViewportService
from .preview_material import PreviewMaterialService
from .material_display import DisplayMaterialService
from .material_override import MaterialOverrideService
from ..core.registry_baker import registry_baker
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bakers.base import BakerBase
    from ..packers.base import PackerBase


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

            data = None
            match BakeVisualizationService.mode():
                case VisualizationMode.PREVIEW:
                    data = PreviewData(producer, bake_group.uuid, baker.uuid)
                case VisualizationMode.DISPLAY:
                    data = DisplayData(bake_group.uuid, baker.accumulated_uuid)
                case _:
                    return

            BakeVisualizationService.refresh(data)

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

            data = PreviewData(producer, bake_group.uuid, baker.uuid)
            BakeVisualizationService.enable_preview(data)
            viz.refreshing = False

        elif viz.enabled_display and viz.mode != "DISPLAY":
            LOG.debug("Enabling Display")
            viz.refreshing = True
            viz.enabled_preview = False
            viz.mode = "DISPLAY"
            data = DisplayData(
                bake_group_uuid=bake_group.uuid,
                accumulated_uuid=baker.accumulated_uuid,
            )

            BakeVisualizationService.enable_display(data)
            viz.refreshing = False


@dataclass(slots=True, frozen=True)
class PreviewData:
    producer: BakerBase | PackerBase
    bake_group_uuid: str
    producer_uuid: str
    accumulated_uuid: str | None = None
    mode: VisualizationMode = VisualizationMode.PREVIEW


@dataclass(slots=True, frozen=True)
class DisplayData:
    bake_group_uuid: str
    accumulated_uuid: str
    producer_uuid: str | None = None
    producer: None = None
    mode: VisualizationMode = VisualizationMode.DISPLAY


class BakeVisualizationService:
    _runtime: VisualizationRuntime | None = None

    # ---------------------------------------------------------
    # State
    # ---------------------------------------------------------

    @classmethod
    def is_active(cls) -> bool:
        return cls._runtime is not None and cls._runtime.active

    @classmethod
    def mode(cls) -> VisualizationMode | None:

        if cls._runtime is None:
            return None

        return cls._runtime.mode

    @classmethod
    def _ensure_runtime(cls):
        if cls._runtime is None:
            from ..runtime.runtime_manager import RuntimeManager

            runtime = RuntimeManager.current(bpy.context)
            cls._runtime = runtime.visualization

    # ---------------------------------------------------------
    # Preview
    # ---------------------------------------------------------

    @classmethod
    def enable_preview(cls, data: PreviewData):
        cls._ensure_runtime()
        if cls.is_active():
            cls.disable()

        cls._begin(data)

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
    def enable_display(cls, data: DisplayData):
        cls._ensure_runtime()

        if cls.is_active():
            cls.disable()

        cls._begin(data)

        ViewportService.set_texture()

    # ---------------------------------------------------------
    # Disable
    # ---------------------------------------------------------

    @classmethod
    def disable(cls):

        if not cls.is_active() or cls._runtime is None:
            return

        LOG.debug("Disabling Visualization")

        try:
            MaterialOverrideService.restore(cls._runtime.material_snapshots)

            ViewportService.restore(cls._runtime)

        finally:
            cls._runtime.clear()

    # ---------------------------------------------------------
    # Refresh
    # ---------------------------------------------------------

    @classmethod
    def refresh(cls, data: DisplayData | PreviewData):

        if not cls.is_active():
            return

        LOG.debug("Refresh Visualization")

        match cls.mode():
            case VisualizationMode.PREVIEW:
                if not isinstance(data, PreviewData):
                    return

                cls.disable()

                cls.enable_preview(data)

            case VisualizationMode.DISPLAY:
                if not isinstance(data, DisplayData):
                    return

                cls.disable()

                cls.enable_display(data)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
    @classmethod
    def _begin(cls, data: PreviewData | DisplayData) -> None:

        if cls._runtime is None:
            return

        # If another visualization is already active,
        # restore it first.

        if cls._runtime.active:
            cls.disable()

        cls._runtime.begin(
            mode=data.mode,
            producer=data.producer,
            bake_group_uuid=data.bake_group_uuid,
            producer_uuid=data.producer_uuid,
            accumulated_uuid=data.accumulated_uuid,
        )

        cls._capture_state(data)

    @classmethod
    def _capture_state(cls, data: PreviewData | DisplayData) -> None:
        LOG.debug("Capture State")
        if cls._runtime is None:
            return

        scenes = ViewportService.capture_state()

        for scene_name, scene_state in scenes.scenes.items():
            cls._runtime.set_scene_state(
                scene_name,
                scene_state,
            )

        if isinstance(data, PreviewData):
            material = PreviewMaterialService.get_or_create()
            data.producer.configure_preview_material(material)

            cls._runtime.set_active_producer(data.producer)
            cls._runtime.set_material_snapshots(MaterialOverrideService.apply(bpy.context.scene.objects, material))
            if data.producer.is_custom:
                cls._runtime.refresh_preview_parameters(force=True)

        else:
            material = DisplayMaterialService.get_or_create()
            image = cls._get_image(data.bake_group_uuid, data.accumulated_uuid)

            if image is None or image.image is None:
                return

            DisplayMaterialService.set_image(
                material,
                image.image,
            )
            cls._runtime.set_active_image_handle(image)
            cls._runtime.set_active_producer(data.producer)
            cls._runtime.set_material_snapshots(MaterialOverrideService.apply(bpy.context.scene.objects, material))
