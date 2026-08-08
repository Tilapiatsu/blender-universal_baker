from __future__ import annotations

from dataclasses import dataclass, field

import bpy

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bakers.base import BakerBase
    from .task_bake import BakeTask
    from .settings_output import OutputSettings
    from .image_handle import ImageHandle

from ..resources.image import ImageResource
from ..resources.material import MaterialResource
from .settings_bake import BakeSettings
from .context import ExecutionContext
from ..properties.project import UBK_Project


@dataclass(slots=True)
class BakeContext(ExecutionContext):
    """Runtime context used while executing a single BakeTask."""

    task: BakeTask
    baker: BakerBase

    image: ImageResource = field(default_factory=ImageResource)
    output: ImageHandle | None = None

    material: MaterialResource = field(default_factory=MaterialResource)
    node_tree: bpy.types.NodeTree | None = None
    image_node: bpy.types.ShaderNodeTexImage | None = None

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
    def target(self) -> bpy.types.Object:
        return self.task.target.object

    @property
    def sources(self) -> tuple[bpy.types.Object]:
        # TODO : Need to fix
        return [o.object for o in self.task.sources]

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
