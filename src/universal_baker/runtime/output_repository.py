from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Generator
from typing import TYPE_CHECKING


from ..constant import LOG
from ..logger_bake_middleware.bake_summary import BakeStatus
from .output_artifact import OutputArtifact
from .artifact_repository import ArtifactRepository
from .image_handle import ImageHandle

if TYPE_CHECKING:
    from ..runtime.bake_group import BakeGroup

LOG_SCOPE = "Output Repository"


class OutputRepository:
    """
    Runtime repository storing every Output produced
    during the execution of a BakeSession.

    Simply indexes and returns ImageHandle instances
    """

    def __init__(self, artifact_repository: ArtifactRepository):
        self._artifacts = artifact_repository
        self._outputs = {}
        self._index_baker = defaultdict(list)
        self._index_target_object = defaultdict(list)
        self._materialized = {}
        self.clear()

    def clear(self) -> None:
        self._outputs: dict[str, ImageHandle] = {}
        self._index_baker = defaultdict(list)
        self._index_target_object = defaultdict(list)

    def add(self, output: ImageHandle) -> None:
        self._outputs[output.uuid] = output

        target_key = (output.bake_group.uuid, output.uuid)

        target_object_key = (output.bake_group.uuid, output.uuid, output.target_object_uuid)
        self._index_baker[target_key].append(output)
        self._index_target_object[target_object_key].append(output)

    def get(self, artifact: OutputArtifact) -> ImageHandle | None:
        if artifact.uuid in self._outputs:
            return self._outputs[artifact.uuid]

        return self._materialize(artifact)

    def remove(self, output: ImageHandle) -> None:
        self._outputs.pop(output.uuid, None)

        target_key = (
            output.bake_group.uuid,
            output.uuid,
        )

        outputs = self._index_baker.get(target_key)

        if outputs and output in outputs:
            outputs.remove(output)

            if not outputs:
                del self._index_baker[target_key]

    def resolve_baker_outputs(
        self,
        bake_group_uuid: str,
        producer_uuid: str,
        materialize: bool = True,
    ) -> list[ImageHandle]:
        with LOG.scope(LOG_SCOPE):
            # First try RAM
            LOG.debug("Resolving Output")
            key = (bake_group_uuid, producer_uuid)

            outputs = self._lookup_baker(key)

            if outputs:
                LOG.debug(f"{len(outputs)} found from memory")
                return outputs

            # Otherwise ask persistent artifacts.
            artifacts = self._artifacts.resolve_baker(bake_group_uuid, producer_uuid)

            LOG.debug(f"{len(artifacts)} found")

            if not artifacts:
                LOG.error(
                    "Artifacts not found",
                    data={
                        "status": BakeStatus.FAIL,
                    },
                )
                return []

            outputs = []

            for artifact in artifacts:
                if materialize:
                    outputs.append(self._materialize(artifact))
                else:
                    outputs.append(artifact)

            return outputs

    def resolve_target_object_outputs(
        self,
        bake_group_uuid: str,
        producer_uuid: str,
        target_object_uuid: str,
        materialize: bool = True,
    ) -> list[ImageHandle]:
        with LOG.scope(LOG_SCOPE):
            # First try RAM
            LOG.debug("Resolving Output")
            key = (bake_group_uuid, producer_uuid, target_object_uuid)

            outputs = self._lookup_target_object(key)

            if outputs:
                LOG.debug(f"{len(outputs)} found from memory")
                return outputs

            # Otherwise ask persistent artifacts.
            artifacts = self._artifacts.resolve_target_object(bake_group_uuid, producer_uuid, target_object_uuid)

            LOG.debug(f"{len(artifacts)} found")

            if not artifacts:
                LOG.error(
                    "Artifacts not found",
                    data={
                        "status": BakeStatus.FAIL,
                    },
                )
                return []

            outputs = []

            for artifact in artifacts:
                if materialize:
                    outputs.append(self._materialize(artifact))
                else:
                    outputs.append(artifact)

            return outputs

    def _lookup_baker(self, key: tuple[str, str]) -> list[ImageHandle]:
        return self._index_baker[key]

    def _lookup_target_object(self, key: tuple[str, str, str]) -> list[ImageHandle]:
        return self._index_target_object[key]

    def iter_outputs(self) -> Iterable[ImageHandle]:
        return self._outputs.values()

    @property
    def count(self) -> int:
        return len(self._outputs)

    def clear_target(self, bake_group: ImageHandle) -> None:
        ids = [output.uuid for output in self.iter_outputs() if output.bake_group == bake_group]

        for output_id in ids:
            self.remove(self._outputs[output_id])

    def iter_bake_group_outputs(self, bake_group: BakeGroup) -> Generator[ImageHandle]:
        for output in self.iter_outputs():
            if output.bake_group == bake_group:
                yield output

    def _materialize(self, artifact: OutputArtifact) -> ImageHandle | None:
        """Get output from memory if exists or create a new one if not."""
        if artifact.uuid in self._materialized:
            LOG.debug("Retreive from Memory")

            return self._outputs[artifact.uuid]

        output = self._create_image_handle(artifact)

        if output is None:
            return None

        self.add(output)

        return output

    def get_outputs(self, bake_group_uuid: str, producer_uuid: str) -> list[ImageHandle]:
        outputs = self._lookup_baker((bake_group_uuid, producer_uuid))

        if outputs:
            return outputs

        outputs = self._load_from_artifacts(bake_group_uuid, producer_uuid)

        return outputs

    def _load_from_artifacts(self, bake_group_uuid: str, producer_uuid: str) -> list[ImageHandle]:
        artifacts = self._artifacts.find_outputs(bake_group_uuid, producer_uuid)

        outputs = []

        for artifact in artifacts:
            output = self._create_image_handle(artifact)
            if output is None:
                continue

            self.add(output)
            outputs.append(output)

        return outputs

    def _create_image_handle(self, artifact: OutputArtifact) -> ImageHandle | None:
        LOG.debug("Create Image Handle from Artifact")

        image_handle = ImageHandle(artifact)
        return image_handle

    def invalidate(self, bake_group_uuid: str, producer_uuid: str) -> None:
        """
        Removes all runtime BakeOutputs associated
        with one target/producer pair.
        """

        outputs = self.resolve_baker_outputs(
            bake_group_uuid,
            producer_uuid,
            materialize=False,
        )

        for output in outputs:
            self.remove(output)

    def clear_materialized(self, artifact_uuid: str):
        output_uuid = self._materialized.pop(artifact_uuid, None)

        if output_uuid is None:
            return

        self.remove(self._outputs[output_uuid])

    # def _max_chr(self) -> dict[str, int]:
    #     max_chr = {"target_name": 0, "bake_id": 0, "uuid": 0}
    #     for id, output in self._outputs.items():
    #         max_chr["target_name"] = max(len(output.target_object_name), max_chr["target_name"])
    #         max_chr["baker_id"] = max(len(output.baker.id), max_chr["bake_id"])
    #         max_chr["uuid"] = max(len(id), max_chr["uuid"])
    #
    #     return max_chr

    def __repr__(self) -> str:
        result = f"Repository contains {self.count} output(s)\n"
        for id, output in self._outputs.items():
            result += f"{str(output):20} | {id}\n"

        return result
