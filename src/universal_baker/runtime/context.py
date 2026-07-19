from __future__ import annotations

from dataclasses import dataclass, field

import bpy


from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..bakers.base import BakerBase
    from .task_bake import BakeTask
    from .task_pack import PackingTask

from ..ressources.image import ImageResource
from ..ressources.material import MaterialResource
from .settings_bake import BakeSettings
from .settings_cage import CageSettings
from .settings_pack import PackSettings

from .session import ExecutionSession


@dataclass(slots=True)
class ExecutionContext:
    def __init__(self, session) -> None:
        self.session = session


@dataclass(slots=True)
class BakeContext(ExecutionContext):
    """Runtime context used while executing a single BakeTask."""

    session: ExecutionSession
    task: BakeTask
    baker: BakerBase
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
    def sources(self) -> tuple[bpy.types.Object]:
        return self.task.sources

    # @property
    # def output_path(self):
    #     return self.task.output_path

    @property
    def selected_to_active(self) -> bool:
        return self.task.selected_to_active

    @property
    def settings(self) -> BakeSettings:
        return self.task.settings

    def succeed(self, message: str = "") -> None:
        self.finished = True
        self.success = True
        self.message = message

    def fail(self, message: str) -> None:
        self.finished = True
        self.success = False
        self.message = message


@dataclass(slots=True)
class PackContext(ExecutionContext):
    session: ExecutionSession
    task: PackingTask
    node_tree: bpy.types.NodeTree | None = None
    image_node: bpy.types.ShaderNodeTexImage | None = None
    image: ImageResource = field(default_factory=ImageResource)

    finished: bool = False
    success: bool = False
    message: str = ""

    @property
    def settings(self) -> PackSettings:
        return self.task.settings

    def succeed(self, message: str = "") -> None:
        self.finished = True
        self.success = True
        self.message = message

    def fail(self, message: str) -> None:
        self.finished = True
        self.success = False
        self.message = message
