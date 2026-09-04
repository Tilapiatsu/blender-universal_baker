from __future__ import annotations

import bpy

from dataclasses import dataclass
from typing import TYPE_CHECKING


from ..constant import LOG
from .task import Task
from .uv_ownership_mask import UvOwnershipMask
from ..enum.image_layout import ImageLayout
from ..logger_bake_middleware.bake_summary import EventCategory, BakeStatus
from ..logger.event import ScopeState
from .context_ownership_mask import OwnershipMaskContext

if TYPE_CHECKING:
    from ..resources.ownership import OwnershipDatas

LOG_SCOPE = "Uv Ownership"


class UvOwnership:
    name: str = "UvOwnership"

    def execute(self, ctx: OwnershipMaskContext) -> UvOwnershipMask:
        with LOG.scope(LOG_SCOPE):
            from ..services.uv_ownership import UvOwnershipService
            # ISSUE:
            # - Baking with Multiple Targets and multiple sources and Cages, and only the first target of the list get baked
            # properly -> Its an issue with the ownership mapsk

            LOG.info("Generting UV Ownership mask")
            result = UvOwnershipService.create_uv_ownership_mask(
                ownership_datas=ctx.task.ownership_datas,
                resolution=(
                    ctx.task.output_context.output_settings.path.width,
                    ctx.task.output_context.output_settings.path.height,
                ),
                name=f"{ctx.task.bake_group_name}_UVOwnership",
                use_udim=ctx.task.uv_layout.image_layout == ImageLayout.UDIM,
            )

            ctx.task.ownership_mask.set(result)

            # NOTE: Saving Map to disk : This is for debug purpose only. Need to be removed !!!
            if True:
                from ..core.output_resolver import OutputResolver
                from ..services.image_codec import ImageCodec

                for o in ctx.task.ownership_datas.values():
                    LOG.debug(f"Writing mask for {o.object_name}")
                    mask = ctx.task.ownership_mask.mask_for_object(o.object_uuid)
                    for tile, buffer in mask.tile_buffers:
                        LOG.debug(f"{tile}")
                        output = OutputResolver.resolve(
                            ctx.task.output_context,
                            ImageLayout.SINGLE,
                            suffix=f"{o.object_name}." + str(tile),
                            sub_folder="Mask",
                        )
                        ImageCodec.save(output.absolute_path, buffer, ctx.task.output_context.output_settings)

            return result


@dataclass(slots=True, frozen=True)
class UvOwnershipTask(Task):
    """
    Generate the UV ownership mask for one target object.
    """

    ownership_datas: OwnershipDatas
    ownership_mask: UvOwnershipMask
    producer: UvOwnership = UvOwnership()
    id: str = "UV_OWNERSHIP"

    @property
    def bake_group_name(self) -> str:
        from ..core.controller import BakeController

        bake_group = BakeController.get_bake_group_from_uuid(self.bake_group_uuid)
        if bake_group is None:
            return ""

        return bake_group.name

    def __repr__(self) -> str:
        result = f"UV_OWNERSHIP_MASK_{self.bake_group_name}"
        return result

    def notify_finished(self, time_elapsed: float) -> None:
        with LOG.scope("Ownership Mask"):
            LOG.info(
                message=f"{self.__repr__()} succeeded",
                category=EventCategory.MASK,
                scope_state=ScopeState.EXIT,
                scope_duration=time_elapsed,
                data={
                    "status": BakeStatus.SUCCESS,
                },
            )

    def notify_failed(self, time_elapsed: float, error: str) -> None:
        with LOG.scope("Ownership Mask"):
            LOG.error(
                message="Ownership Mask failed",
                category=EventCategory.MASK,
                scope_state=ScopeState.EXIT,
                scope_duration=time_elapsed,
                data={
                    "status": BakeStatus.FAIL,
                },
            )
            LOG.error(
                message=error,
                category=EventCategory.BAKE,
                data={
                    "status": BakeStatus.FAIL,
                },
            )
