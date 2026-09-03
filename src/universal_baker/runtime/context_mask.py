from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..runtime.image_handle import ImageHandle
    from .output_repository import OutputRepository
    from .settings_output import OutputSettings
    from .task_mask_buffer import MaskBufferTask

import bpy

from ..properties.project import UBK_Project
from ..resources.image import ImageResource
from ..runtime.uv_ownership_mask import UvOwnershipMask
from .context import ExecutionContext


@dataclass(slots=True)
class MaskContext(ExecutionContext):
    """Runtime context used while executing a single MaskTask."""

    task: MaskBufferTask

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
    def mask(self) -> UvOwnershipMask:
        return self.task.uv_ownership_task.ownership_mask

    def get_input_image_handles(self, repository: OutputRepository) -> list[ImageHandle]:
        return repository.resolve_target_object_outputs(
            self.task.bake_group_uuid, self.task.baker_uuid, self.task.target_object_uuid
        )

    def succeed(self, message: str = "") -> None:
        self.finished = True
        self.success = True
        self.message = message

    def fail(self, message: str) -> None:
        self.finished = True
        self.success = False
        self.message = message
