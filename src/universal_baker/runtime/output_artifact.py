from __future__ import annotations

import bpy

from pathlib import Path
from typing import TYPE_CHECKING
from datetime import datetime

from ..services.image_io import ImageIOService

if TYPE_CHECKING:
    from bpy.types import Scene
    from ..runtime.image_buffer import ImageBuffer
    from ..properties.artifact import UBK_Artifact


class OutputArtifact:
    """
    Runtime wrapper around a persistent UBK_PG_Artifact.
    """

    def __init__(self, scene: Scene, artifact: UBK_Artifact):
        self.scene = scene
        self.data = artifact

    @property
    def uuid(self):
        return self.data.uuid

    @property
    def producer_id(self):
        return self.data.producer_id

    @property
    def target_uid(self):
        return self.data.target_uid

    @property
    def path(self) -> Path:
        return Path(bpy.path.abspath(self.data.relative_path))

    @property
    def exists(self) -> bool:
        return self.path.exists()

    def load(self) -> ImageBuffer:
        """
        Loads the artifact from disk.
        """

        return ImageIOService.load(self.path)

    def delete(self):

        if self.exists:
            self.path.unlink()

    @property
    def dependencies(self):

        return [dep.artifact_uid for dep in self.data.dependencies]

    @property
    def timestamp(self):

        if not self.data.created:
            return None

        return datetime.fromisoformat(self.data.created)
