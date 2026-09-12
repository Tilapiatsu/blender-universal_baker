from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import bpy

from ..constant import LOG
from ..core.registry_definition import registry_definition
from ..parameter.parameter_applier import ParameterApplier
from ..parameter.parameter_context import ParameterContext


@dataclass(slots=True)
class ObjectVisibilityState:
    name: str
    hide_viewport: bool
    hide_get: bool


@dataclass(slots=True)
class CageVisualizationRuntime:
    active: bool = False

    target_uuid: str | None = None
    target_name: str | None = None
    cage_name: str | None = None

    # Original object visibility.
    visibility: dict[str, ObjectVisibilityState] = field(default_factory=dict)

    # Original active object / mode.
    active_object_name: str | None = None
    active_object_mode: str = "OBJECT"

    # Temporary collection.
    temporary_collection_name: str | None = None
    owns_temporary_collection: bool = False

    # Objects that this service linked to the temporary collection.
    #
    # We only remove links that we created ourselves.
    temporary_links: set[str] = field(default_factory=set)

    # Objects involved in the visualization.
    source_object_names: list[str] = field(default_factory=list)
    target_object_names: list[str] = field(default_factory=list)

    # GPU resources.
    draw_handler: object | None = None

    surface_shader: object | None = None
    wire_shader: object | None = None

    surface_batch: object | None = None
    wire_batch: object | None = None

    # The cage datablock may change its evaluated geometry while
    # weight painting. The GPU batches therefore need to be rebuilt.
    gpu_dirty: bool = False

    # Last evaluated dependency-graph update state.
    evaluated_cage_revision: int = 0

    _preview_dirty: bool = False
    _updating_parameters: bool = False

    def begin(
        self,
        *,
        target_uuid: str,
        target_name: str,
        cage_name: str,
    ) -> None:
        self.active = True
        self.target_uuid = target_uuid
        self.target_name = target_name
        self.cage_name = cage_name
        self.gpu_dirty = True

    def mark_gpu_dirty(self) -> None:
        self.gpu_dirty = True

    def clear(self) -> None:
        self.active = False

        self.target_uuid = None
        self.target_name = None
        self.cage_name = None

        self.visibility.clear()

        self.active_object_name = None
        self.active_object_mode = "OBJECT"

        self.temporary_collection_name = None
        self.owns_temporary_collection = False
        self.temporary_links.clear()

        self.source_object_names.clear()
        self.target_object_names.clear()

        self.draw_handler = None

        self.surface_shader = None
        self.wire_shader = None

        self.surface_batch = None
        self.wire_batch = None

        self.gpu_dirty = False
        self.evaluated_cage_revision = 0

    def request_preview_refresh(self):
        self._preview_dirty = True

    def refresh_preview_parameters(
        self,
        ui_props: Any | None = None,
        force: bool = False,
    ):
        """Make sure the UI property element binds propely to the material, modifier or geometry node element defined in
        the custom baker definition asset"""

        LOG.debug("Refresging Parameter")
        if not force:
            if not self._preview_dirty:
                return

            if self._updating_parameters:
                return

        try:
            self._updating_parameters = True

            definition = registry_definition.get_local("CAGE")

            if definition is None:
                LOG.error("Definition not found")
                return

            if not self.active or self.target_uuid is None or self.cage_name is None:
                return

            from ..services.parameter_service import ParameterService

            snapshot = ParameterService.snapshot_regular(definition, ui_props)

            cage = bpy.data.objects.get(self.cage_name)

            if cage is None:
                LOG.error("Cage not found")

            context = ParameterContext(
                object=cage,
                is_dragging=bpy.context.scene.ubk_project.visualization.is_dragging,
            )

            ParameterApplier.apply_regular(definition, snapshot, context)

        finally:
            self._updating_parameters = False
            self._preview_dirty = False
