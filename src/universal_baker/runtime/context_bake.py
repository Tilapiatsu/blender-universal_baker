from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import bpy

if TYPE_CHECKING:
    from ..bakers.base import BakerBase
    from .image_handle import ImageHandle
    from .settings_output import OutputSettings
    from .task_bake import BakeTask

from ..properties.project import UBK_Project
from ..resources.image import ImageResource
from ..resources.material import MaterialResources
from .context import ExecutionContext
from .settings_bake import BakeSettings


@dataclass(slots=True)
class BakeContext(ExecutionContext):
    """Runtime context used while executing a single BakeTask."""

    task: BakeTask
    baker: BakerBase

    image: ImageResource = field(default_factory=ImageResource)
    output: ImageHandle | None = None

    target_materials: dict[str, MaterialResources] = field(default_factory=dict)
    sources_materials: dict[str, MaterialResources] = field(default_factory=dict)
    node_tree: bpy.types.NodeTree | None = None
    image_node: bpy.types.ShaderNodeTexImage | None = None

    _target: bpy.types.Object | None = None
    _sources: list[bpy.types.Object] | None = None

    finished: bool = False
    success: bool = False
    message: str = ""

    @property
    def project(self) -> UBK_Project:
        return bpy.context.scene.ubk_project

    @property
    def blender_context(self) -> bpy.types.Context:
        return self.session.context

    @property
    def scene(self) -> bpy.types.Scene:
        return self.session.context.scene

    @property
    def baker_material_objects(self) -> list[bpy.types.Object]:
        if self.selected_to_active:
            return self.sources
        else:
            return [self.target]

    @property
    def baker_materials(self):
        if self.selected_to_active:
            return self.sources_materials
        else:
            return self.target_materials

    @property
    def target(self) -> bpy.types.Object:
        if self._target is None:
            self._target = self.task.target.object

        return self._target

    @target.setter
    def target(self, value: bpy.types.Object) -> None:
        self._target = value

    @property
    def sources(self) -> list[bpy.types.Object]:
        if self._sources is None:
            self._sources = self.task.sources

        return self._sources

    @sources.setter
    def sources(self, sources) -> None:
        self._sources = sources

    @property
    def selected_to_active(self) -> bool:
        return self.task.selected_to_active

    @property
    def settings(self) -> BakeSettings:
        return self.task.settings

    @property
    def output_settings(self) -> OutputSettings:
        return self.task.output_context.output_settings

    def succeed(self, message: str = "") -> None:
        self.finished = True
        self.success = True
        self.message = message

    def fail(self, message: str) -> None:
        self.finished = True
        self.success = False
        self.message = message
