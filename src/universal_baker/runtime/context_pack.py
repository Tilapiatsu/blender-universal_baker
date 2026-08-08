from __future__ import annotations

from dataclasses import dataclass, field

import bpy

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .task_pack import PackingTask
    from ..resources.pack import PackResource
    from .settings_output import OutputSettings
    from ..runtime.tile_set import TileSet
    from .image_handle import ImageHandle

from ..resources.image import ImageResource
from .context import ExecutionContext
from ..properties.project import UBK_Project
from .settings_pack import PackSettings


@dataclass(slots=True)
class PackContext(ExecutionContext):
    """Runtime context used while executing a single PackTask."""

    task: PackingTask
    node_tree: bpy.types.NodeTree | None = None
    image_node: bpy.types.ShaderNodeTexImage | None = None

    image: ImageResource = field(default_factory=ImageResource)
    inputs: list[ImageHandle] | None = None
    output: ImageHandle | None = None

    red_buffer: TileSet | None = None
    green_buffer: TileSet | None = None
    blue_buffer: TileSet | None = None
    alpha_buffer: TileSet | None = None

    pack_red: bool = False
    pack_green: bool = False
    pack_blue: bool = False
    pack_alpha: bool = False

    output_buffer: TileSet | None = None
    pack_resource: PackResource | None = None

    finished: bool = False
    success: bool = False
    message: str = ""

    @property
    def project(self) -> UBK_Project:
        return bpy.context.scene.ubk_project

    @property
    def settings(self) -> PackSettings:
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
