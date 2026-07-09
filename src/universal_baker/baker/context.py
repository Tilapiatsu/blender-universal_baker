from __future__ import annotations

from dataclasses import dataclass, field

import bpy

from .base import BaseBaker
from ..ressources.image import ImageResource
from ..ressources.material import MaterialResource

from .session import BakeSession
from .task import BakeTask


@dataclass(slots=True)
class BakeContext:
    """Runtime context used while executing a single BakeTask."""

    session: BakeSession
    task: BakeTask
    baker: BaseBaker

    image: ImageResource = field(default_factory=ImageResource)
    material: MaterialResource = field(default_factory=MaterialResource)
    node_tree: bpy.types.NodeTree | None = None
    image_node: bpy.types.ShaderNodeTexImage | None = None

    finished: bool = False
    success: bool = False
    message: str = ""

    @property
    def blender_context(self) -> bpy.types.Context:
        return self.session.context

    @property
    def scene(self) -> bpy.types.Scene:
        return self.session.context.scene

    @property
    def target(self) -> bpy.types.Object:
        return self.task.target

    @property
    def sources(self) -> list[bpy.types.Object]:
        return self.task.sources

    @property
    def output(self):
        return self.task.output

    @property
    def selected_to_active(self) -> bool:
        return self.task.selected_to_active

    def succeed(self, message: str = "") -> None:
        self.finished = True
        self.success = True
        self.message = message

    def fail(self, message: str) -> None:
        self.finished = True
        self.success = False
        self.message = message
