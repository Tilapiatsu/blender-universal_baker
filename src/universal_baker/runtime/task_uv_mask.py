from __future__ import annotations

import bpy

from dataclasses import dataclass
from typing import TYPE_CHECKING


from ..constant import LOG
from .task import Task
from ..enum.image_layout import ImageLayout

if TYPE_CHECKING:
    from .tile_set import TileSet

LOG_SCOPE = "Uv Mask"


@dataclass(slots=True, frozen=True)
class UvMaskTask(Task):
    """
    Generate the UV ownership mask for one target object.

    This is a transient task:
        - it does not create an OutputArtifact
        - it does not register anything in ArtifactRepository
        - its result only exists for the duration of the execution
    """

    target_object: str
    uv_layer: str

    def execute(self, context: bpy.types.Context) -> TileSet:
        with LOG.scope(LOG_SCOPE):
            obj = context.scene.objects.get(self.target_object)

            if obj is None:
                message = f"Cannot generate UV mask: object {self.target_object!r} no longer exists."
                LOG.error(message)
                raise RuntimeError(message)

            from ..services.uv_ownership import UvOwnershipService

            LOG.info(f"Generting UV Mask for {self.uv_layer}")
            result = UvOwnershipService.create_mask(
                obj=obj,
                resolution=(
                    self.output_context.output_settings.path.width,
                    self.output_context.output_settings.path.height,
                ),
                uv_map=self.uv_layer,
                use_udim=self.uv_layout.image_layout == ImageLayout.UDIM,
                name=f"{obj.name}_{self.uv_layer}_UVOwnership",
            )

            self.result.set_tileset(result, clear=True)

            from ..services.image_codec import ImageCodec
            from ..core.output_resolver import OutputResolver

            for tile, buffer in self.result.tile_buffers:
                LOG.debug(f"{buffer.name}_{tile}")
                output = OutputResolver.resolve(
                    self.output_context, ImageLayout.SINGLE, suffix=buffer.name + str(tile), sub_folder="Mask"
                )
                ImageCodec.save(output.absolute_path, buffer, self.output_context.output_settings)

            return result

    def __repr__(self) -> str:
        result = f"UV_MASK_{self.target_object} | {self.uv_layer:100} "
        return result
