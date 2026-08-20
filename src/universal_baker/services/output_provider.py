from __future__ import annotations


from ..constant import LOG
from ..runtime.image_handle import ImageHandle
from ..logger_bake_middleware.bake_summary import BakeStatus

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..runtime.output_repository import OutputRepository

LOG_SCOPE = "Output Provider"


class OutputProvider:
    """
    High-level access to runtime bake results.

    Responsible for:
        - retrieving OutputBakes
        - accumulating grouped targets
        - caching accumulated images
    """

    def __init__(self, repository: OutputRepository):
        self._repository = repository

        #
        # (bake_group_uuid, baker_uuid) -> ImageBuffer
        #
        self._cache = {}

    def clear(self):
        self._cache.clear()

    def invalidate(self, bake_group_uuid: str | None = None, baker_uuid: str | None = None):
        """
        Removes cached images.

        If no arguments are given every cache entry is removed.
        """

        if bake_group_uuid is None and baker_uuid is None:
            self.clear()
            return

        keys = []

        for key in self._cache:
            t, b = key

            if bake_group_uuid is not None and t != bake_group_uuid:
                continue

            if baker_uuid is not None and b != baker_uuid:
                continue

            keys.append(key)

        for key in keys:
            self._cache.pop(key, None)

    def get_producer_image(self, bake_group_uuid: str, producer_uuid: str) -> list[ImageHandle] | None:
        with LOG.scope(LOG_SCOPE):
            LOG.debug("Request Image from repository")

            # ISSUE : Cached image is a bit too dumb right now. If the user change the resolution for exemple, the
            # cached version will be considered valid and reterned but the size will be wrong.
            # TODO : Need to store other metadata like resolution with cached buffer in order to invalidate the cached
            # if the metadata differes from the requested image
            #
            # Cached ?
            #
            # key = (bake_group_uuid, producer_uuid)
            # cached = self._cache.get(key)
            #
            # if cached is not None:
            #     LOG.debug("Reuse cached image")
            #     return cached

            outputs = self._repository.resolve_baker_outputs(bake_group_uuid, producer_uuid)

            if not outputs:
                LOG.error(
                    "Output not found",
                    data={
                        "status": BakeStatus.FAIL,
                    },
                )
                return None

            LOG.debug(f"{len(outputs)} image(s) found :")
            for o in outputs:
                LOG.debug(o.artifact.name)

            return outputs

    def get_target_object_image(
        self, bake_group_uuid: str, producer_uuid: str, target_object_uuid: str
    ) -> list[ImageHandle] | None:
        with LOG.scope(LOG_SCOPE):
            LOG.debug("Request Image from repository")
            outputs = self._repository.resolve_target_object_outputs(bake_group_uuid, producer_uuid, target_object_uuid)
            if not outputs:
                LOG.error(
                    "Output not found",
                    data={
                        "status": BakeStatus.FAIL,
                    },
                )
                return None

            LOG.debug(f"{len(outputs)} image(s) found :")
            for o in outputs:
                LOG.debug(o.artifact.name)

            return outputs

    def has_image(self, bake_group_uuid: str, baker_uuid: str) -> bool:
        return (
            self.get_producer_image(
                bake_group_uuid,
                baker_uuid,
            )
            is not None
        )

    def preload(self, bake_group_uuid: str):
        """
        Pre-build every baked map for a target.

        Useful before packing.
        """

        bakers = {
            output.uuid for output in self._repository.iter_outputs() if output.bake_group.uuid == bake_group_uuid
        }

        for baker in bakers:
            self.get_producer_image(bake_group_uuid, baker)
