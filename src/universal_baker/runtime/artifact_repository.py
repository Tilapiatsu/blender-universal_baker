from __future__ import annotations

from collections import defaultdict

import bpy

from ..constant import LOG
from .output_artifact import OutputArtifact
from ..properties.project import UBK_Project


LOG_SCOPE = "Artifact Repository"


class ArtifactRepository:
    """
    Runtime view over the persistent artifact database.
    Answers where the logical image lives and how it's named (including UDIM expansion)
    """

    def __init__(self, scene: bpy.types.Scene, project: UBK_Project) -> None:
        self.scene = scene
        self.project = project

        self.rebuild()

    def rebuild(self) -> None:
        self._artifacts: dict[str, OutputArtifact] = {}
        self._bake_group_index = defaultdict(list)
        self._producer_index = defaultdict(list)
        self._target_object_index = defaultdict(list)

        for pg in self.project.artifacts:
            artifact = OutputArtifact(self.scene, pg)

            self._artifacts[artifact.uuid] = artifact
            self._bake_group_index[artifact.bake_group_uuid].append(artifact)
            self._producer_index[artifact.producer_uuid].append(artifact)
            self._target_object_index[artifact.target_object_uuid].append(artifact)

    def all(self) -> list[OutputArtifact]:
        return list(self._artifacts.values())

    def get(self, uuid: str) -> OutputArtifact | None:
        return self._artifacts.get(uuid)

    def by_bake_group(self, bake_group_uuid: str) -> list[OutputArtifact]:
        return list(self._bake_group_index.get(bake_group_uuid, []))

    def by_producer(self, producer_uuid: str) -> list[OutputArtifact]:
        return list(self._producer_index.get(producer_uuid, []))

    def by_target(self, target_object_uuid: str) -> list[OutputArtifact]:
        return list(self._target_object_index.get(target_object_uuid, []))

    def resolve_baker(self, bake_group_uuid: str, producer_uuid: str) -> list[OutputArtifact]:
        with LOG.scope(LOG_SCOPE):
            LOG.debug("Resolving Output")
            return [
                artifact for artifact in self.by_bake_group(bake_group_uuid) if artifact.producer_uuid == producer_uuid
            ]

    def resolve_target_object(
        self,
        bake_group_uuid: str,
        producer_uuid: str,
        target_object_uuid: str,
    ) -> list[OutputArtifact]:
        with LOG.scope(LOG_SCOPE):
            LOG.debug("Resolving Output")
            return [
                artifact
                for artifact in self.by_bake_group(bake_group_uuid)
                if artifact.producer_uuid == producer_uuid and artifact.target_object_uuid == target_object_uuid
            ]

    def exists(self, bake_group_uuid: str, producer_uuid: str) -> bool:
        return any(
            artifact.exists
            for artifact in self.by_bake_group(bake_group_uuid)
            if artifact.producer_uuid == producer_uuid
        )

    def remove(self, uuid: str) -> None:
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
