from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter

import bpy

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .job import BakeJob
    from .task import BakeTask


class SessionContext:
    def __init__(self, session: BakeSession):
        self.session = session

    @property
    def scene(self):
        return self.session.context.scene

    @property
    def task(self):
        return self.session.current_task


@dataclass(slots=True)
class BakeSession:
    """Runtime execution state for a BakeJob."""

    job: BakeJob
    context: bpy.types.Context
    current_task: BakeTask | None = None
    cancelled: bool = False
    start_time: float = field(default_factory=perf_counter)
    original_mode: str = "OBJECT"
    original_active_object: bpy.types.Object | None = None
    original_selected_objects: list[bpy.types.Object] = field(default_factory=list)

    original_engine: str = ""
    original_samples: int = 0
    original_margin: int = 16
    original_margin_type: str = ""

    temporary_images: list[bpy.types.Image] = field(default_factory=list)
    temporary_materials: list[bpy.types.Material] = field(default_factory=list)
    temporary_node_groups: list[bpy.types.NodeTree] = field(default_factory=list)

    def initialize(self, context: bpy.types.Context) -> None:
        """Capture the current Blender state."""

        self.capture_scene(context)
        self.capture_render_settings(context)

    def capture_scene(self, context: bpy.types.Context) -> None:
        self.original_mode = context.mode
        self.original_active_object = context.view_layer.objects.active
        self.original_selected_objects = list(context.selected_objects)

    def capture_render_settings(self, context: bpy.types.Context) -> None:
        scene = context.scene
        cycles = scene.cycles

        self.original_engine = scene.render.engine
        self.original_samples = cycles.samples

        self.original_margin = scene.render.bake.margin
        self.original_margin_type = scene.render.bake.margin_type

    def restore(self, context: bpy.types.Context) -> None:
        """Restore Blender to its original state."""

        self.restore_render_settings(context)
        self.restore_scene(context)

    def restore_render_settings(self, context: bpy.types.Context) -> None:
        scene = context.scene
        cycles = scene.cycles

        scene.render.engine = self.original_engine

        cycles.samples = self.original_samples

        scene.render.bake.margin = self.original_margin
        scene.render.bake.margin_type = self.original_margin_type

    def restore_scene(self, context: bpy.types.Context) -> None:
        bpy.ops.object.select_all(action="DESELECT")

        for obj in self.original_selected_objects:
            if obj.name in bpy.data.objects:
                obj.select_set(True)

        context.view_layer.objects.active = self.original_active_object

        try:
            if self.original_active_object is not None and context.mode != self.original_mode:
                bpy.ops.object.mode_set(mode=self.original_mode)

        except RuntimeError:
            # Some modes cannot always be restored (e.g. Sculpt after deletion).
            pass

    def register_image(self, image: bpy.types.Image) -> None:
        self.temporary_images.append(image)

    def register_material(self, material: bpy.types.Material) -> None:
        self.temporary_materials.append(material)

    def register_node_group(self, node_tree: bpy.types.NodeTree) -> None:
        self.temporary_node_groups.append(node_tree)

    def cleanup(self) -> None:
        """Delete every temporary datablock created during the bake."""

        for image in self.temporary_images:
            if image.users == 0:
                bpy.data.images.remove(image)

        for material in self.temporary_materials:
            if material.users == 0:
                bpy.data.materials.remove(material)

        for node_tree in self.temporary_node_groups:
            if node_tree.users == 0:
                bpy.data.node_groups.remove(node_tree)

        self.temporary_images.clear()
        self.temporary_materials.clear()
        self.temporary_node_groups.clear()

    def cancel(self) -> None:
        self.cancelled = True

    @property
    def is_cancelled(self) -> bool:
        return self.cancelled

    @property
    def elapsed_time(self) -> float:
        return perf_counter() - self.start_time
