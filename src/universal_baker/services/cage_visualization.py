from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import bpy

from ..constant import LOG
from ..runtime.runtime_visualization_cage import CageVisualizationRuntime


@dataclass(slots=True)
class CageVisualizationState:
    source_visibility: dict[str, bool]
    target_visibility: dict[str, bool]

    active_object_name: str | None
    active_mode: str | None

    cage_object_name: str | None
    cage_collection_name: str | None

    draw_handler: object | None = None


@dataclass(slots=True, frozen=True)
class DisplayData:
    bake_group_uuid: str
    target_uuid: str
    cage_object: bpy.types.Object


class CageVisualizationService:
    _runtime: CageVisualizationRuntime | None = None

    # ---------------------------------------------------------
    # State
    # ---------------------------------------------------------

    @classmethod
    def is_active(cls) -> bool:
        return cls._runtime is not None and cls._runtime.active

    @classmethod
    def _ensure_runtime(cls):
        if cls._runtime is None:
            from ..runtime.runtime_manager import RuntimeManager

            runtime = RuntimeManager.current(bpy.context)
            cls._runtime = runtime.cage_visualization

    # ---------------------------------------------------------
    # Display
    # ---------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
    @classmethod
    def _begin(cls, data: DisplayData) -> None:

        if cls._runtime is None:
            return

        # If another visualization is already active,
        # restore it first.

        if cls._runtime.active:
            cls.disable()

        cls._runtime.begin(
            bake_group_uuid=data.bake_group_uuid,
            target_uuid=data.target_uuid,
            cage_object=data.cage_object.name,
        )

        cls._capture_state(data)

    @classmethod
    def _capture_state(cls, data: DisplayData) -> None:
        LOG.debug("Capture State")
        if cls._runtime is None:
            return

        scenes = ViewportService.capture_state()

        for scene_name, scene_state in scenes.scenes.items():
            cls._runtime.set_scene_state(
                scene_name,
                scene_state,
            )

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
