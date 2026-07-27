from __future__ import annotations

from collections import defaultdict

import bpy

from .output_artifact import OutputArtifact
from ..properties.project import UBK_Project


class ArtifactRepository:
    """
    Runtime view over the persistent artifact database.
    """

    def __init__(self, scene: bpy.types.Scene, project: UBK_Project) -> None:
        self.scene = scene
        self.project = project

        self.rebuild()

    def rebuild(self) -> None:
        self._artifacts: dict[str, OutputArtifact] = {}
        self._bake_group_index = defaultdict(list)
        self._producer_index = defaultdict(list)

        for pg in self.project.artifacts:
            artifact = OutputArtifact(self.scene, pg)

            self._artifacts[artifact.uuid] = artifact
            self._bake_group_index[artifact.bake_group_uuid].append(artifact)
            self._producer_index[artifact.producer_uuid].append(artifact)

    def all(self) -> list[OutputArtifact]:
        return list(self._artifacts.values())

    def get(self, uuid) -> OutputArtifact | None:
        return self._artifacts.get(uuid)

    def by_bake_group(self, bake_group_uuid) -> list[OutputArtifact]:
        return list(self._bake_group_index.get(bake_group_uuid, []))

    def by_producer(self, producer_uuid) -> list[OutputArtifact]:
        return list(self._producer_index.get(producer_uuid, []))

    def resolve(self, bake_group_uuid: str, producer_uuid: str) -> list[OutputArtifact]:
        return [artifact for artifact in self.by_bake_group(bake_group_uuid) if artifact.producer_uuid == producer_uuid]

    def exists(self, bake_group_uuid, producer_uuid) -> bool:
        return any(
            artifact.exists
            for artifact in self.by_bake_group(bake_group_uuid)
            if artifact.producer_uuid == producer_uuid
        )

    def remove(self, uuid) -> None:
        artifact = self._artifacts.get(uuid)

        if artifact is None:
            return

        # Remove PropertyGroup

        for i, item in enumerate(self.project.artifacts):
            if item.uuid == uuid:
                self.project.artifacts.remove(i)

                break

        self.rebuild()

    def find_outputs(self, bake_group_uuid: str, producer_uuid: str) -> list[OutputArtifact]:
        return [
            artifact for artifact in self._bake_group_index[bake_group_uuid] if artifact.producer_uuid == producer_uuid
        ]

    def clear(self) -> None:
        self.project.artifacts.clear()
        self.rebuild()
