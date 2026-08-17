from __future__ import annotations

from dataclasses import dataclass, field

import bpy

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .settings_output import OutputSettings
    from .tile_set import TileSet
    from .task_ownership_mask import UvOwnershipTask

from ..constant import LOG
from .context import ExecutionContext
from ..properties.project import UBK_Project


@dataclass(slots=True)
class OwnershipMaskContext(ExecutionContext):
    """Runtime context used while executing a single MaskTask."""

    task: UvOwnershipTask

    finished: bool = False
    success: bool = False
    message: str = ""

    @property
    def project(self) -> UBK_Project:
        return bpy.context.scene.ubk_project

    @property
    def scene(self) -> bpy.types.Scene:
        return bpy.context.scene

    @property
    def output_settings(self) -> OutputSettings:
        return self.task.output_context.output_settings

    @property
    def mask(self) -> TileSet:
        return self.task.result

    def succeed(self, message: str = "") -> None:
        self.finished = True
        self.success = True
        self.message = message

    def fail(self, message: str) -> None:
        self.finished = True
        self.success = False
        self.message = message
