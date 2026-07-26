from __future__ import annotations

from collections import defaultdict

import bpy

from .output_artifact import OutputArtifact
from ..properties.project import UBK_Project


class ArtifactRepository:
    """
    Runtime view over the persistent artifact database.
    """

    def __init__(self, scene: bpy.types.Scene, project: UBK_Project):
        self.scene = scene
        self.project = project

        self.rebuild()

    def rebuild(self):
        self._artifacts = {}
        self._baker_group_index = defaultdict(list)
        self._producer_index = defaultdict(list)

        for pg in self.project.artifacts:
            artifact = OutputArtifact(self.scene, pg)

            self._artifacts[artifact.uuid] = artifact
            self._baker_group_index[artifact.bake_group_uuid].append(artifact)
            self._producer_index[artifact.producer_uuid].append(artifact)

    def all(self):
        return self._artifacts.values()

    def get(self, uuid):
        return self._artifacts.get(uuid)

    def by_bake_group(self, bake_group_uuid):
        return list(self._baker_group_index.get(bake_group_uuid, []))

    def by_producer(self, producer_id):
        return list(self._producer_index.get(producer_id, []))

    def resolve(self, bake_group_uuid: str, producer_id: str):
        return [artifact for artifact in self.by_bake_group(bake_group_uuid) if artifact.producer_id == producer_id]

    def exists(self, target_uid, producer_id):
        return any(
            artifact.exists for artifact in self.by_bake_group(target_uid) if artifact.producer_id == producer_id
        )

    def remove(self, uuid):
        artifact = self._artifacts.get(uuid)

        if artifact is None:
            return

        # Remove PropertyGroup

        for i, item in enumerate(self.project.artifacts):
            if item.uuid == uuid:
                self.project.artifacts.remove(i)

                break

        self.rebuild()

    def clear(self):
        self.project.artifacts.clear()
        self.rebuild()
