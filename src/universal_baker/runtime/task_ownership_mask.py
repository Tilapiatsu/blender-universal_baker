from __future__ import annotations

import bpy

from dataclasses import dataclass
from typing import TYPE_CHECKING


from ..constant import LOG
from .task import Task
from .uv_ownership_mask import UvOwnershipMask
from ..enum.image_layout import ImageLayout

if TYPE_CHECKING:
    from ..resources.ownership import OwnershipData

LOG_SCOPE = "Uv Ownership"


# TODO : Need to finish writing of UVOwnershipTask to generate a UvOwnershipMask which will be used to create ImageMask
# to mask each bakes output


@dataclass(slots=True, frozen=True)
class UvOwnershipTask(Task):
    """
    Generate the UV ownership mask for one target object.
    """

    target_objects: list[OwnershipData]
    ownership_mask: UvOwnershipMask

    @property
    def bake_group_name(self) -> str:
        from ..core.controller import BakeController

        bake_group = BakeController.get_bake_group_from_uuid(self.bake_group_uuid)
        if bake_group is None:
            return ""

        return bake_group.name

    def execute(self, context: bpy.types.Context) -> UvOwnershipMask:
        with LOG.scope(LOG_SCOPE):
            from ..services.uv_ownership import UvOwnershipService

            LOG.info("Generting UV Ownership mask")
            result = UvOwnershipService.create_uv_ownership_mask(
                target_objects=self.target_objects,
                resolution=(
                    self.output_context.output_settings.path.width,
                    self.output_context.output_settings.path.height,
                ),
                name=f"{self.bake_group_name}_UVOwnership",
                use_udim=self.uv_layout.image_layout == ImageLayout.UDIM,
            )

            self.ownership_mask.set(result)

            # NOTE: Saving Map to disk : This is for debug purpose only. Need to be removed !!!
            from ..services.image_codec import ImageCodec
            from ..core.output_resolver import OutputResolver

            for o in self.target_objects:
                LOG.debug(f"Writing mask for {o.object_name}")
                mask = self.ownership_mask.mask_for_object(o.object_uuid)
                for tile, buffer in mask.tile_buffers:
                    LOG.debug(f"{tile}")
                    output = OutputResolver.resolve(
                        self.output_context,
                        ImageLayout.SINGLE,
                        suffix=f"{o.object_name}." + str(tile),
                        sub_folder="Mask",
                    )
                    ImageCodec.save(output.absolute_path, buffer, self.output_context.output_settings)

            return result

    def __repr__(self) -> str:
        result = f"UV_OWNERSHIP_MASK_{self.bake_group_name}"
        return result
