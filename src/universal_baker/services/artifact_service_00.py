from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable
from uuid import uuid4

import bpy

from ..runtime.output_artifact import OutputArtifact


class ArtifactService:
    """
    Responsible for creating, updating and removing
    persistent output artifacts.

    This is the ONLY class allowed to modify
    project.artifacts.
    """

    # ---------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------

    @staticmethod
    def _find(project, bake_group_uuid: str, producer_uuid: str):

        for artifact in project.artifacts:
            if artifact.bake_group_uuid == bake_group_uuid and artifact.producer_uuid == producer_uuid:
                return artifact

        return None

    @staticmethod
    def _fill_metadata(
        artifact,
        *,
        artifact_type,
        bake_group_uuid,
        producer_uuid,
        path,
        image,
        checksum="",
    ):
        path = Path(path)

        artifact.type = artifact_type
        artifact.target_uid = bake_group_uuid
        artifact.producer_uuid = producer_uuid

        artifact.relative_path = bpy.path.relpath(str(path))
        artifact.filename = path.stem
        artifact.extension = path.suffix

        artifact.width = image.width
        artifact.height = image.height
        artifact.channels = image.channels

        artifact.file_format = image.file_format
        artifact.color_space = image.color_space

        artifact.checksum = checksum

        artifact.created = datetime.now().isoformat()

    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------

    @classmethod
    def register(
        cls,
        *,
        project,
        artifact_type,
        bake_group_uuid,
        producer_uuid,
        path,
        image,
        dependencies: Iterable[str] = (),
        checksum="",
    ) -> OutputArtifact:
        """
        Creates or updates an artifact.

        Registration behaves like an UPSERT.
        """

        artifact = cls._find(project, bake_group_uuid, producer_uuid)

        #
        # Existing artifact
        #

        if artifact is None:
            artifact = project.artifacts.add()
            artifact.uid = str(uuid4())

        cls._fill_metadata(
            artifact,
            artifact_type=artifact_type,
            bake_group_uuid=bake_group_uuid,
            producer_uuid=producer_uuid,
            path=path,
            image=image,
            checksum=checksum,
        )

        artifact.dependencies.clear()

        for uid in dependencies:
            dep = artifact.dependencies.add()
            dep.artifact_uid = uid

        return OutputArtifact(
            bpy.context.scene,
            artifact,
        )

    # ---------------------------------------------------------
    # Removal
    # ---------------------------------------------------------

    @staticmethod
    def remove(project, uid):
        for index, artifact in enumerate(project.artifacts):
            if artifact.uid == uid:
                project.artifacts.remove(index)
                return True

        return False

    @classmethod
    def remove_target(cls, project, bake_group_uuid):
        removed = 0

        for index in reversed(range(len(project.artifacts))):
            artifact = project.artifacts[index]

            if artifact.bake_group_uuid == bake_group_uuid:
                project.artifacts.remove(index)
                removed += 1

        return removed

    @classmethod
    def remove_producer(cls, project, producer_uuid):
        removed = 0

        for index in reversed(range(len(project.artifacts))):
            artifact = project.artifacts[index]

            if artifact.producer_uuid == producer_uuid:
                project.artifacts.remove(index)

                removed += 1

        return removed

    # ---------------------------------------------------------

    @classmethod
    def remove_missing(cls, project):
        removed = 0

        for index in reversed(range(len(project.artifacts))):
            artifact = project.artifacts[index]

            path = Path(bpy.path.abspath(artifact.relative_path))

            if not path.exists():
                project.artifacts.remove(index)

                removed += 1

        return removed

    # ---------------------------------------------------------

    @classmethod
    def clear(cls, project):
        project.artifacts.clear()

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    @staticmethod
    def exists(project, bake_group_uuid, producer_uuid) -> bool:
        return ArtifactService._find(project, bake_group_uuid, producer_uuid) is not None

    # ---------------------------------------------------------

    @staticmethod
    def find(project, bake_group_uuid, producer_uuid):
        artifact = ArtifactService._find(project, bake_group_uuid, producer_uuid)

        if artifact is None:
            return None

        return OutputArtifact(
            bpy.context.scene,
            artifact,
        )

    # ---------------------------------------------------------

    @staticmethod
    def find_target(project, bake_group_uuid):
        return [
            OutputArtifact(
                bpy.context.scene,
                artifact,
            )
            for artifact in project.artifacts
            if artifact.target_uid == bake_group_uuid
        ]

    # ---------------------------------------------------------

    @staticmethod
    def rebuild(repository):
        """
        Convenience helper to rebuild runtime indexes.
        """
        repository.rebuild()
