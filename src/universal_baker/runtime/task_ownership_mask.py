from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..constant import LOG, UBK_SUBFOLDER_MASK
from ..enum.image_layout import ImageLayout
from ..logger.blender import TaskProgress
from ..logger.scopes.task_status import ScopeState
from ..logger_bake_middleware.bake_summary import BakeStatus, EventCategory
from .context_ownership_mask import OwnershipMaskContext
from .task import OutputTask
from .uv_ownership_mask import UvOwnershipMask

if TYPE_CHECKING:
    from ..resources.ownership import OwnershipDatas

LOG_SCOPE = "Uv Ownership"


class UvOwnership:
    name: str = "UvOwnership"

    def execute(self, ctx: OwnershipMaskContext):
        from ..services.uv_ownership import UvOwnershipService

        LOG.info("Generting UV Ownership mask", display_in_ui=True)
        result = UvOwnershipService.create_uv_ownership_mask(
            ownership_datas=ctx.task.ownership_datas,
            bake_objects=ctx.session.bake_objects,
            resolution=(
                ctx.task.output_context.output_settings.path.width,
                ctx.task.output_context.output_settings.path.height,
            ),
            name=f"{ctx.task.bake_group_name}_UVOwnership",
            use_udim=ctx.task.uv_layout.image_layout == ImageLayout.UDIM,
        )

        ctx.task.ownership_mask.set(result)
        yield TaskProgress(1.0, f"UV Ownership {ctx.task.bake_group_name}")

        # NOTE: Saving Map to disk : This is for debug purpose only
        # Need to link to a global debug parameter
        if True:
            from ..core.output_resolver import OutputResolver
            from ..services.image_codec import ImageCodec

            for o in ctx.task.ownership_datas.values():
                LOG.debug(f"Writing mask for {o.object_name}")
                mask = ctx.task.ownership_mask.mask_for_object(o.object_uuid)
                if mask is None:
                    continue
                for tile, buffer in mask.tile_buffers:
                    LOG.debug(f"{tile}")
                    output = OutputResolver.resolve(
                        ctx.task.output_context,
                        ImageLayout.SINGLE,
                        suffix=f"{o.object_name}." + str(tile),
                        sub_folder=UBK_SUBFOLDER_MASK,
                    )
                    ImageCodec.save(output.absolute_path, buffer, ctx.task.output_context.output_settings, False)

        return "UV Ownership Complete"


@dataclass(slots=True, frozen=True)
class UvOwnershipTask(OutputTask):
    """
    Generate the UV ownership mask for one target object.
    """

    ownership_datas: OwnershipDatas
    ownership_mask: UvOwnershipMask
    producer: UvOwnership = UvOwnership()
    id: str = "UV_OWNERSHIP"

    @property
    def bake_group_name(self) -> str:
        bake_group = self.bake_group
        if bake_group is None:
            return ""

        return bake_group.name

    def __repr__(self) -> str:
        result = f"UV_OWNERSHIP_MASK_{self.bake_group_name}"
        return result

    def notify_finished(self, time_elapsed: float) -> None:
        LOG.info(
            message=f"{self.__repr__()} succeeded",
            category=EventCategory.MASK,
            scope_state=ScopeState.EXIT,
            scope_duration=time_elapsed,
            data={
                "status": BakeStatus.SUCCESS,
            },
            display_in_ui=True,
        )

    def notify_failed(self, time_elapsed: float, error: str) -> None:
        LOG.error(
            message="Ownership Mask failed",
            category=EventCategory.MASK,
            scope_state=ScopeState.EXIT,
            scope_duration=time_elapsed,
            data={
                "status": BakeStatus.FAIL,
            },
            display_in_ui=True,
        )
        LOG.error(
            message=error,
            category=EventCategory.BAKE,
            data={
                "status": BakeStatus.FAIL,
            },
            display_in_ui=True,
        )
