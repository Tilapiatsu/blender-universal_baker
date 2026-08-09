from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from universal_baker.core.output_resolver import OutputResolver

from ..maskers.base import MaskerBase
from .task_uv_mask import UvMaskTask

from .task import Task


@dataclass(slots=True, frozen=True)
class MaskTask(Task):
    uv_mask_task: UvMaskTask
    baker_uuid: str
    masker: MaskerBase
    has_multiple_targets: bool

    @property
    def output_name(self) -> str:
        return f"{self.uv_mask_task.target_object}_{self.masker.name}"

    @property
    def absolute_filepath(self) -> Path:
        file_output = OutputResolver.resolve(
            self.output_context,
            self.uv_layout.image_layout,
            self.uv_mask_task.target_object,
            "object_buffers" if self.has_multiple_targets else None,
        )

        return file_output.absolute_path

    def __repr__(self) -> str:
        result = f"MASK_{self.masker.id} | {self.uv_mask_task.target_object}"
        return result
