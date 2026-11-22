from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from ..core.output_resolver import OutputResolver
from ..logger.scopes.task_scope import TaskScope

if TYPE_CHECKING:
    from ..properties.bake_group import UBK_BakeGroup
    from ..resources.uv import UVLayout
    from ..runtime.color_management_info import ColorManagementInfo
    from .output_context import OutputContext
    from .tile_set import TileSet


@dataclass(slots=True, frozen=True)
class Task:
    """Base Task Class. This is the base class that each executor uses."""

    uuid: str
    name: str
    enabled: bool
    bake_group_uuid: str
    scope: TaskScope

    @property
    def bake_group(self) -> UBK_BakeGroup | None:
        from ..core.controller import BakeController

        return BakeController.get_bake_group_from_uuid(self.bake_group_uuid)

    def __repr__(self) -> str:
        return f"{self.name} Task"

    def notify_finished(self, time_elapsed: float) -> None: ...

    def notify_failed(self, time_elapsed: float, error: str) -> None: ...


@dataclass(slots=True, frozen=True)
class OutputTask(Task):
    """Base Task Class. This is the base class that each executor uses."""

    output_context: OutputContext
    color_management_info: ColorManagementInfo
    uv_layout: UVLayout
    result: TileSet

    @property
    def output_name(self) -> str:
        return self.name

    @property
    def absolute_filepath(self) -> Path:
        file_output = OutputResolver.resolve(self.output_context, self.uv_layout.image_layout)
        return file_output.absolute_path


@dataclass(slots=True)
class TaskResult:
    """Every Task Return a TaskResult."""

    success: bool
    outputs: list[Path]
    warnings: list[str]
    errors: list[str]
