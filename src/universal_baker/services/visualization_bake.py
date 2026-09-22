from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import bpy

from ..constant import LOG
from ..core.registry_baker import registry_baker
from ..enum.visualization import BakeVisualizationMode
from ..runtime.image_handle import ImageHandle
from ..runtime.runtime_visualization_bake import BakeVisualizationRuntime
from ..services.visibility_override import VisibilityOverride
from .material_display import DisplayMaterialService
from .material_override import MaterialOverrideService
from .preview_material import PreviewMaterialService
from .temp_collection import TempCollection
from .viewport import ViewportService

if TYPE_CHECKING:
    from ..bakers.base import BakerBase
    from ..packers.base import PackerBase

TEMP_COLLECTION_NAME = "UBK_PREVIEW_VISUALIZATION"


def set_preview_enabled(value: bool, set_mode=False):
    from ..core.controller import BakeController

    project = BakeController.project(bpy.context)

    viz = project.visualization

    viz.refreshing = True
    viz.enabled_preview = value
    if set_mode:
        viz.mode = "PREVIEW"
    viz.refreshing = False


def set_display_enabled(value: bool, set_mode=False):
    from ..core.controller import BakeController

    project = BakeController.project(bpy.context)

    viz = project.visualization

    viz.refreshing = True
    viz.enabled_display = value
    if set_mode:
        viz.mode = "DISPLAY"
    viz.refreshing = False


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
            BakeVisualizationService.disable()

            return

        # possibly need to refresh only when preview or display is ON:
        # (viz.enabled_preview or viz.enabled_display) and
        if viz.baker_idx != bake_group.active_baker_index:
            viz.baker_idx = bake_group.active_baker_index
            producer = registry_baker[baker.baker]

            data = None
            match BakeVisualizationService.mode():
                case BakeVisualizationMode.PREVIEW:
                    data = PreviewData(producer, bake_group.uuid, baker.uuid)
                case BakeVisualizationMode.DISPLAY:
                    data = DisplayData(
                        bake_group.uuid,
                        baker.accumulated_uuid,
                        [o.object for o in bake_group.target_objects],
                        producer,
                    )
                case BakeVisualizationMode.PREVIEW_CAGE:
                    if BakeVisualizationService.projection_target() is None:
                        return
                    data = PreviewData(
                        producer,
                        bake_group.uuid,
                        baker.uuid,
                        mode=BakeVisualizationMode.PREVIEW_CAGE,
                        projection_target=BakeVisualizationService.projection_target(),
                    )
                case _:
                    return

            if not BakeVisualizationService.refresh(data):
                viz.enabled_display = False
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
    mode: BakeVisualizationMode = BakeVisualizationMode.PREVIEW
    projection_target: bpy.types.Object | None = None


@dataclass(slots=True, frozen=True)
class DisplayData:
    bake_group_uuid: str
    accumulated_uuid: str
    objects: list[bpy.types.Object]
    producer: BakerBase | PackerBase
    producer_uuid: str | None = None
    mode: BakeVisualizationMode = BakeVisualizationMode.DISPLAY


class BakeVisualizationService:
    _runtime: BakeVisualizationRuntime | None = None

    # ---------------------------------------------------------
    # State
    # ---------------------------------------------------------

    @classmethod
    def is_active(cls) -> bool:
        return cls._runtime is not None and cls._runtime.active

    @classmethod
    def mode(cls) -> BakeVisualizationMode | None:

        if cls._runtime is None:
            return None

        return cls._runtime.mode

    @classmethod
    def _ensure_runtime(cls):
        if cls._runtime is None:
            from ..runtime.runtime_manager import RuntimeManager

            runtime = RuntimeManager.current(bpy.context)
            cls._runtime = runtime.bake_visualization

    @classmethod
    def projection_target(cls) -> bpy.types.Object | None:
        cls._ensure_runtime()
        return cls._runtime.projection_target

    # ---------------------------------------------------------
    # Preview
    # ---------------------------------------------------------

    @classmethod
    def enable_preview(cls, data: PreviewData):
        cls._ensure_runtime()
        if cls.is_active():
            cls.disable(set_display_property=False)

        cls._begin(data)

        # Cycles
        bpy.context.scene.render.engine = "CYCLES"

        ViewportService.set_rendered(data.producer.viewport_render_pass, data.producer.color_management_info)

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
            cls.disable(set_display_property=False)

        cls._begin(data)

        ViewportService.set_texture()

    # ---------------------------------------------------------
    # Disable
    # ---------------------------------------------------------

    @classmethod
    def disable(cls, set_display_property: bool = True):

        if not cls.is_active() or cls._runtime is None:
            return

        LOG.debug("Disabling Visualization")

        try:
            cls._revert_object_visibility()
            cls._cleanup_temp_collection()
            cls._revert_image_colorspace()

            MaterialOverrideService.restore(cls._runtime.material_snapshots)
            ViewportService.restore(cls._runtime)

        finally:
            cls._runtime.clear()
            if set_display_property:
                from ..core.controller import BakeController

                project = BakeController.project(bpy.context)
                viz = project.visualization
                viz.refreshing = True
                viz.enabled_display = False
                viz.enabled_preview = False
                viz.mode = "NONE"
                viz.refreshing = False

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
            case BakeVisualizationMode.PREVIEW:
                if not isinstance(data, PreviewData):
                    return False

                cls.disable(set_display_property=False)

                cls.enable_preview(data)

            case BakeVisualizationMode.PREVIEW_CAGE:
                if not isinstance(data, PreviewData):
                    return False

                cls.disable(set_display_property=False)

                cls.enable_preview(data)

            case BakeVisualizationMode.DISPLAY:
                if not isinstance(data, DisplayData):
                    return False

                cls.disable(set_display_property=False)

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
            cls.disable(set_display_property=False)

        # from ..services.visualization_cage import CageVisualizationService
        #
        # CageVisualizationService.disable()
        #
        cls._runtime.begin(
            mode=data.mode,
            producer=data.producer,
            bake_group_uuid=data.bake_group_uuid,
            producer_uuid=data.producer_uuid,
            accumulated_uuid=data.accumulated_uuid,
            objects=[o.name for o in data.objects] if isinstance(data, DisplayData) else [],
            projection_target=data.projection_target if isinstance(data, PreviewData) else None,
        )

        cls._capture_state(data)

    @classmethod
    def _capture_state(cls, data: PreviewData | DisplayData) -> None:
        LOG.debug("Capture State")
        if cls._runtime is None:
            return

        scenes = ViewportService.capture_state()

        # ISSUE: Chaning bake settings and running bake while having display visualization enable makes the
        # visualization lost and getting a white image. Certainely due to the output provider, or because when
        # suspending it stored the old producer uuid and resuming visualization lead to get a invalid producer due to
        # the deprecated uuid ?

        # TODO: Preview Parameters doesn't work in selected to active mode
        for scene_name, scene_state in scenes.scenes.items():
            cls._runtime.set_scene_state(
                scene_name,
                scene_state,
            )

        if isinstance(data, PreviewData):
            cls._runtime.set_object_visibilities(cls._prepare_objects_preview_visibility())
            cls._set_object_visibility()
            cls._runtime.set_temp_collection(cls._prepare_temp_collection())
            cls._create_temp_collection()

            if data.producer.clear_preview_material:
                material = PreviewMaterialService.get_or_create()
                data.producer.configure_preview_material(material)
                if PreviewData.projection_target is None and data.mode == BakeVisualizationMode.PREVIEW_CAGE:
                    raise RuntimeError("Cage Projection Target is None")
                elif data.projection_target is not None and data.mode == BakeVisualizationMode.PREVIEW_CAGE:
                    mat_override_objects = [o for o in bpy.context.scene.objects if o != data.projection_target]
                else:
                    mat_override_objects = bpy.context.scene.objects

                cls._runtime.set_material_snapshots(MaterialOverrideService.apply(mat_override_objects, material))

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

            DisplayMaterialService.set_image(material, image.image, data.producer.image_colorspace)

            cls._runtime.set_active_image_handle(handle)
            cls._runtime.set_active_producer(data.producer)
            cls._runtime.set_material_snapshots(MaterialOverrideService.apply(data.objects, material))

    @classmethod
    def _prepare_temp_collection(cls) -> TempCollection:

        from ..core.controller import BakeController

        bake_group = BakeController.active_bake_group(bpy.context)
        if bake_group is None:
            raise RuntimeError("No active Bake Group")

        objects = []
        for target in bake_group.target_objects:
            if target.have_source:
                objects += target.source_object_list
                continue

            if target.object is None:
                continue

            objects.append(target.object)

        collection = TempCollection(TEMP_COLLECTION_NAME, objects)

        return collection

    @classmethod
    def _prepare_objects_preview_visibility(cls) -> list[VisibilityOverride]:

        from ..core.controller import BakeController

        overrides = []
        bake_group = BakeController.active_bake_group(bpy.context)
        if bake_group is None:
            raise RuntimeError("No active Bake Group")

        for target in bake_group.target_objects:
            if not target.have_source:
                visibility_override = VisibilityOverride(target.object, hide_viewport=False)
                continue

            visibility_override = VisibilityOverride(target.object, hide_viewport=True)
            overrides.append(visibility_override)

            for source in target.source_object_list:
                visibility_override = VisibilityOverride(source, hide_viewport=False)
                overrides.append(visibility_override)

        return overrides

    @classmethod
    def _set_object_visibility(cls):
        if cls._runtime is None:
            return

        for ov in cls._runtime.object_visibilities:
            ov.set_visibility()

    @classmethod
    def _revert_object_visibility(cls):
        if cls._runtime is None:
            return

        for ov in cls._runtime.object_visibilities:
            ov.revert_visibility()

    @classmethod
    def _create_temp_collection(cls):
        if cls._runtime is None or cls._runtime.temp_collection is None:
            return

        cls._runtime.temp_collection.create()

    @classmethod
    def _cleanup_temp_collection(cls):
        if cls._runtime is None or cls._runtime.temp_collection is None:
            return

        cls._runtime.temp_collection.cleanup()
