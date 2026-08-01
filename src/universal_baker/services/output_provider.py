from __future__ import annotations

from universal_baker.logger_bake_middleware.bake_summary import BakeStatus

from ..core.accumulator import ImageAccumulator
from ..core.registry_compositor import registry_compositor
from ..constant import LOG

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..runtime.image_buffer import ImageBuffer
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

    def get_image(self, bake_group_uuid: str, baker_uuid: str) -> ImageBuffer | None:
        with LOG.scope(LOG_SCOPE):
            LOG.debug("Request Image from repository")
            key = (bake_group_uuid, baker_uuid)

            #
            # Cached ?
            #
            cached = self._cache.get(key)

            if cached is not None:
                LOG.debug("Reuse cached image")
                return cached

            outputs = self._repository.resolve_outputs(bake_group_uuid, baker_uuid)

            if not outputs:
                LOG.error(
                    "Output not found",
                    data={
                        "status": BakeStatus.FAIL,
                    },
                )
                return None

            LOG.debug(f"{len(outputs)} image(s) found :")
            #
            # Single object target
            #
            if len(outputs) == 1:
                image = outputs[0].image

                self._cache[key] = image

                return image

    def has_image(self, bake_group_uuid: str, baker_uuid: str) -> bool:

        return (
            self.get_image(
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
            self.get_image(bake_group_uuid, baker)
