from __future__ import annotations

from dataclasses import dataclass, field

import bpy

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .image_buffer import ImageBuffer
    from .settings_output import OutputSettings

from ..constant import LOG
from .context import ExecutionContext
from ..properties.project import UBK_Project
from ..resources.image import ImageResource
from ..runtime.settings_accumulate import AccumulateSettings
from ..runtime.task_accumulate import AccumulateTask
from ..logger_bake_middleware.bake_summary import EventCategory


@dataclass(slots=True)
class AccumulateContext(ExecutionContext):
    """Runtime context used while executing a single AccumulateTask."""

    task: AccumulateTask
    input_buffers: list[ImageBuffer] | None = None
    output_buffer: ImageBuffer | None = None

    node_tree: bpy.types.NodeTree | None = None
    image_node: bpy.types.ShaderNodeTexImage | None = None

    image: ImageResource = field(default_factory=ImageResource)

    finished: bool = False
    success: bool = False
    message: str = ""

    @property
    def project(self) -> UBK_Project:
        return bpy.context.scene.ubk_project

    @property
    def settings(self) -> AccumulateSettings:
        return self.task.settings

    @property
    def output_settings(self) -> OutputSettings:
        return self.task.output_context.output_settings

    def get_input_images(self) -> list[bpy.types.Image] | list:
        from ..core.controller import BakeController

        baker = BakeController.get_baker_from_uuid(self.task.baker_uuid)

        if baker is None:
            LOG.error(
                "Baker not found",
                category=EventCategory.ACCUMULATE,
            )
            return []

        input_images = [i.image for i in baker.images]

        return input_images

    def succeed(self, message: str = "") -> None:
        self.finished = True
        self.success = True
        self.message = message

    def fail(self, message: str) -> None:
        self.finished = True
        self.success = False
        self.message = message
