from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


from ..maskers.base import MaskerBase
from ..core.output_resolver import OutputResolver
from ..runtime.task_ownership_mask import UvOwnershipTask

from .task import Task


@dataclass(slots=True, frozen=True)
class MaskBufferTask(Task):
    uv_ownership_task: UvOwnershipTask
    baker_uuid: str
    target_object_uuid: str
    producer: MaskerBase
    has_multiple_targets: bool

    id: str = "MASK"

    @property
    def output_name(self) -> str:
        return f"{self.uv_ownership_task.name}_{self.producer.name}"

    @property
    def absolute_filepath(self) -> Path:
        file_output = OutputResolver.resolve(
            self.output_context,
            self.uv_layout.image_layout,
            self.uv_ownership_task.name,
            "object_buffers" if self.has_multiple_targets else None,
        )

        return file_output.absolute_path

    def __repr__(self) -> str:
        result = f"MASK_{self.producer.id} | {self.uv_ownership_task.name}"
        return result
