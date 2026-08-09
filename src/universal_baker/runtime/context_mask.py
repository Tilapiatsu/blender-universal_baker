from __future__ import annotations

from dataclasses import dataclass, field

import bpy

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .output_repository import OutputRepository
    from .settings_output import OutputSettings
    from ..runtime.image_handle import ImageHandle
    from .task_mask import MaskTask
    from .tile_set import TileSet

from ..constant import LOG
from .context import ExecutionContext
from ..properties.project import UBK_Project
from ..resources.image import ImageResource


@dataclass(slots=True)
class MaskContext(ExecutionContext):
    """Runtime context used while executing a single MaskTask."""

    task: MaskTask

    image: ImageResource = field(default_factory=ImageResource)
    inputs: list[ImageHandle] | None = None
    output: ImageHandle | None = None

    node_tree: bpy.types.NodeTree | None = None
    image_node: bpy.types.ShaderNodeTexImage | None = None

    finished: bool = False
    success: bool = False
    message: str = ""

    @property
    def project(self) -> UBK_Project:
        return bpy.context.scene.ubk_project

    @property
    def output_settings(self) -> OutputSettings:
        return self.task.output_context.output_settings

    @property
    def mask(self) -> TileSet:
        return self.task.uv_mask_task.result

    def get_input_image_handles(self, repository: OutputRepository) -> list[ImageHandle]:
        return repository.resolve_outputs(self.task.bake_group_uuid, self.task.baker_uuid)

    def succeed(self, message: str = "") -> None:
        self.finished = True
        self.success = True
        self.message = message

    def fail(self, message: str) -> None:
        self.finished = True
        self.success = False
        self.message = message
