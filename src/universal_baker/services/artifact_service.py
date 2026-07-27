from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import Iterable

from ..runtime.output_artifact import OutputArtifact


class ArtifactService:
    """
    Synchronizes persistent artifact metadata with runtime repositories.

    This is the ONLY class allowed to modify
    project.artifacts.
    """

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    @classmethod
    def register(
        cls,
        runtime,
        project,
        *,
        artifact_type,
        bake_group,
        producer,
        file_path,
        width,
        height,
        channels,
        color_space,
        file_format,
        checksum="",
        dependencies: Iterable[str] = (),
    ) -> OutputArtifact:
        """
        Creates or updates an artifact.
        """

        file_path = Path(file_path)

        artifact_pg = cls._find_property_group(
            project,
            bake_group.uuid,
            producer.uuid,
        )

        #
        # Existing artifact ?
        #
        if artifact_pg is None:
            artifact_pg = project.artifacts.add()

            artifact_pg.uid = cls._generate_uuid()

        #
        # Fill metadata
        #

        artifact_pg.type = artifact_type
        artifact_pg.bake_group_uuid = bake_group.uuid
        artifact_pg.producer_uuid = producer.uuid
        artifact_pg.relative_path = str(file_path)
        artifact_pg.filename = file_path.name
        artifact_pg.extension = file_path.suffix.lower()
        artifact_pg.width = width
        artifact_pg.height = height
        artifact_pg.channels = channels
        artifact_pg.color_space = color_space
        artifact_pg.file_format = file_format
        artifact_pg.checksum = checksum
        artifact_pg.created = datetime.now().isoformat()

        #
        # Dependencies
        #

        artifact_pg.dependencies.clear()

        for uuid in dependencies:
            dep = artifact_pg.dependencies.add()

            dep.artifact_uuid = uuid

        #
        # Runtime refresh
        #

        runtime.artifacts.rebuild()

        runtime.outputs.invalidate(
            bake_group.uuid,
            producer.uuid,
        )

        return runtime.artifacts.get(artifact_pg.uuid)

    # ------------------------------------------------------------------
    # Removal
    # ------------------------------------------------------------------

    @classmethod
    def remove(
        cls,
        runtime,
        project,
        artifact_uuid,
        delete_file=False,
    ):

        artifact = runtime.artifacts.get(artifact_uuid)

        if artifact is None:
            return

        if delete_file:
            artifact.delete()

        for i, item in enumerate(project.artifacts):
            if item.uid == artifact_uuid:
                project.artifacts.remove(i)

                break

        runtime.artifacts.rebuild()

        runtime.outputs.clear_materialized(artifact_uuid)

    @classmethod
    def remove_target(
        cls,
        runtime,
        project,
        bake_group_uuid,
        delete_files=False,
    ):

        artifacts = list(runtime.artifacts.by_target(bake_group_uuid))

        for artifact in artifacts:
            cls.remove(runtime, project, artifact.uuid, delete_files)

    @classmethod
    def remove_producer(
        cls,
        runtime,
        project,
        producer_uuid,
        delete_files=False,
    ):

        artifacts = list(runtime.artifacts.by_producer(producer_uuid))

        for artifact in artifacts:
            cls.remove(runtime, project, artifact.uuid, delete_files)

    @classmethod
    def validate(
        cls,
        runtime,
        project,
    ):
        """
        Removes artifacts whose files no longer exist.
        """

        for artifact in list(runtime.artifacts.all()):
            if artifact.exists():
                continue

            cls.remove(runtime, project, artifact.uuid, delete_file=False)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _find_property_group(
        project,
        bake_group_uuid,
        producer_uuid,
    ):

        for artifact in project.artifacts:
            if artifact.bake_group_uuid == bake_group_uuid and artifact.producer_uuid == producer_uuid:
                return artifact

        return None

    @staticmethod
    def _generate_uuid():

        from uuid import uuid4

        return str(uuid4())
