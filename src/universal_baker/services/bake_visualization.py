from __future__ import annotations

import bpy

from ..runtime.visualization_state import (
    VisualizationState,
)

from .viewport import ViewportService
from .preview_material import (
    PreviewMaterialService,
)
from .material_display import (
    DisplayMaterialService,
)
from .material_override import (
    MaterialOverrideService,
)


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
        baker,
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

    @classmethod
    def enable_display(
        cls,
        image: bpy.types.Image,
    ):

        if cls.is_active():
            cls.disable()

        cls._state = ViewportService.capture_state()

        cls._state.active = True
        cls._state.mode = "DISPLAY"

        material = DisplayMaterialService.get_or_create()

        DisplayMaterialService.set_image(
            material,
            image,
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
        baker=None,
        image=None,
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
            if image is None:
                return

            cls.disable()

            cls.enable_display(image)
