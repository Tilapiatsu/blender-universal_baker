from __future__ import annotations

from dataclasses import dataclass

import bpy

from ..constant import LOG

from ..runtime.runtime_visualization import VisualizationRuntime
from ..runtime.image_handle import ImageHandle
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

        # possibly need to refresh only when preview or display is ON:
        # (viz.enabled_preview or viz.enabled_display) and
        if viz.baker_idx != bake_group.active_baker_index:
            viz.baker_idx = bake_group.active_baker_index
            producer = registry_baker[baker.baker]

            data = None
            match BakeVisualizationService.mode():
                case VisualizationMode.PREVIEW:
                    data = PreviewData(producer, bake_group.uuid, baker.uuid)
                case VisualizationMode.DISPLAY:
                    data = DisplayData(
                        bake_group.uuid,
                        baker.accumulated_uuid,
                        [o.object for o in bake_group.target_objects],
                        producer,
                    )
                case _:
                    return

            if not BakeVisualizationService.refresh(data):
                viz.enabled_display = False
                viz.enabled_preview = False
                viz.enabled_preview = False
                viz.mode = "NONE"

            return

        elif not viz.enabled_preview and not viz.enabled_display:
            viz.mode = "NONE"
            BakeVisualizationService.disable()
            return

        producer = registry_baker[baker.baker]

        if viz.enabled_preview and viz.mode != "PREVIEW":
            LOG.debug("Enabling Preview")
            viz.refreshing = True
            viz.enabled_display = False
            viz.mode = "PREVIEW"

            data = PreviewData(producer, bake_group.uuid, baker.uuid)

            BakeVisualizationService.enable_preview(data)

        elif viz.enabled_display and viz.mode != "DISPLAY":
            LOG.debug("Enabling Display")
            viz.refreshing = True
            viz.enabled_preview = False
            viz.mode = "DISPLAY"
            data = DisplayData(
                bake_group_uuid=bake_group.uuid,
                accumulated_uuid=baker.accumulated_uuid,
                objects=[o.object for o in bake_group.target_objects],
                producer=producer,
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
    objects: list[bpy.types.Object]
    producer: BakerBase | PackerBase
    producer_uuid: str | None = None
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
        bpy.context.scene.render.engine = "CYCLES"

        ViewportService.set_rendered(data.producer.viewport_render_pass, data.producer.view_transform)

    # ---------------------------------------------------------
    # Display
    # ---------------------------------------------------------

    @classmethod
    def _get_image(cls, bake_group_uuid: str, baker_uuid: str) -> bpy.types.Image | None:
        handle = cls._get_image_handle(bake_group_uuid, baker_uuid)

        if handle is None:
            return None

        image = handle.image()

        return image

    @staticmethod
    def _get_image_handle(bake_group_uuid: str, baker_uuid: str) -> ImageHandle | None:
        from ..runtime.runtime_manager import RuntimeManager

        runtime = RuntimeManager.current(bpy.context)

        handles = runtime.provider.get_producer_image(bake_group_uuid=bake_group_uuid, producer_uuid=baker_uuid)

        if handles is None:
            return

        if len(handles) > 1:
            LOG.warning(f"{len(handles)} handles found.")

        return handles[0]

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
            cls._revert_image_colorspace()

            MaterialOverrideService.restore(cls._runtime.material_snapshots)
            ViewportService.restore(cls._runtime)

        finally:
            cls._runtime.clear()

    @classmethod
    def _revert_image_colorspace(cls):
        if not cls.is_active() or cls._runtime is None:
            return

        if cls._runtime.active_image_handle is not None:
            colorspace = cls._runtime.active_image_handle._output_settings.color.colorspace
            bake_group_uuid = cls._runtime.bake_group_uuid
            accumulated_uuid = cls._runtime.accumulated_uuid
            if bake_group_uuid is not None and accumulated_uuid is not None:
                image = cls._get_image(bake_group_uuid, accumulated_uuid)
                if image is not None and image.image is not None:
                    image.image.colorspace_settings.name = colorspace

    # ---------------------------------------------------------
    # Refresh
    # ---------------------------------------------------------

    @classmethod
    def refresh(cls, data: DisplayData | PreviewData) -> bool:

        if not cls.is_active():
            return False

        LOG.debug("Refresh Visualization")

        match cls.mode():
            case VisualizationMode.PREVIEW:
                if not isinstance(data, PreviewData):
                    return False

                cls.disable()

                cls.enable_preview(data)

            case VisualizationMode.DISPLAY:
                if not isinstance(data, DisplayData):
                    return False

                cls.disable()

                if cls._get_image_handle(data.bake_group_uuid, data.accumulated_uuid) is None:
                    return False

                cls.enable_display(data)

        return True

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
            objects=[o.name for o in data.objects] if isinstance(data, DisplayData) else [],
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
            if data.producer.clear_preview_material:
                material = PreviewMaterialService.get_or_create()
                data.producer.configure_preview_material(material)
                cls._runtime.set_material_snapshots(MaterialOverrideService.apply(bpy.context.scene.objects, material))

            cls._runtime.set_active_producer(data.producer)

            if data.producer.is_custom:
                cls._runtime.refresh_preview_parameters(force=True)

        else:
            # TODO: Investigate slight contrast difference beetween the preview and display of baked images
            material = DisplayMaterialService.get_or_create()

            handle = cls._get_image_handle(data.bake_group_uuid, data.accumulated_uuid)
            image = cls._get_image(data.bake_group_uuid, data.accumulated_uuid)

            if handle is None or image is None or image.image is None:
                return

            DisplayMaterialService.set_image(material, image.image, data.producer.image_colorspace.value)

            cls._runtime.set_active_image_handle(handle)
            cls._runtime.set_active_producer(data.producer)
            cls._runtime.set_material_snapshots(MaterialOverrideService.apply(data.objects, material))
