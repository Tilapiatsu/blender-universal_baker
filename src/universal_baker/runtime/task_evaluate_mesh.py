from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import bpy

if TYPE_CHECKING:
    from ..properties.bake_group import UBK_BakeGroup

from ..constant import LOG
from ..runtime.context_evaluated_mesh import EvaluatedMeshContext
from ..runtime.evaluated_meshes import EvaluatedMeshes
from ..logger.event import ScopeState
from ..logger_bake_middleware.bake_summary import BakeStatus, EventCategory
from .task import Task

LOG_SCOPE = "Evaluate Targets"


class EvaluateMeshes:
    name: str = "Evaluate Targets"

    def execute(self, ctx: EvaluatedMeshContext) -> EvaluatedMeshes:
        with LOG.scope(LOG_SCOPE):
            LOG.info("Evaluating Meshes")
            result = EvaluatedMeshes()
            return result


@dataclass(slots=True, frozen=True)
class EvaluateMeshesTask(Task):
    evaluated_targets: EvaluatedMeshes
    producer: EvaluateMeshes = EvaluateMeshes()
    id: str = "EVALUATE_TARGETS"

    @property
    def bake_group(self) -> UBK_BakeGroup | None:
        from ..core.controller import BakeController

        return BakeController.get_bake_group_from_uuid(self.bake_group_uuid)

    def __repr__(self) -> str:
        result = f"{self.id}"
        return result

    def notify_finished(self, time_elapsed: float) -> None:
        with LOG.scope("Baking"):
            LOG.info(
                message=f"{self.producer.name} succeeded",
                category=EventCategory.EVALUATE_TARGETS,
                scope_state=ScopeState.EXIT,
                scope_duration=time_elapsed,
                data={
                    "status": BakeStatus.SUCCESS,
                },
            )

    def notify_failed(self, time_elapsed: float, error: str) -> None:
        with LOG.scope("Baking"):
            LOG.error(
                message=f"{self.producer.name} failed",
                category=EventCategory.EVALUATE_TARGETS,
                scope_state=ScopeState.EXIT,
                scope_duration=time_elapsed,
                data={
                    "status": BakeStatus.FAIL,
                },
            )
            LOG.error(
                message=error,
                category=EventCategory.EVALUATE_TARGETS,
                data={
                    "status": BakeStatus.FAIL,
                },
            )
