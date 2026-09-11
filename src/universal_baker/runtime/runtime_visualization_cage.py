from __future__ import annotations

from dataclasses import dataclass, field


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
