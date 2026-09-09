from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .context_evaluate_mesh import EvaluateMeshesContext


from ..constant import LOG
from ..logger.event import ScopeState
from ..logger_bake_middleware.bake_summary import BakeStatus, EventCategory
from .evaluated_meshes import EvaluatedMeshDatas, EvaluateMeshes
from .task import Task

LOG_SCOPE = "Evaluate Meshes"


class StoreEvaluateMeshes:
    name: str = "Evaluate Meshes"

    def execute(self, ctx: EvaluateMeshesContext) -> EvaluateMeshes:
        with LOG.scope(LOG_SCOPE):
            LOG.info("Evaluating Meshes")
            result = EvaluateMeshes()

            for mesh in ctx.task.evaluated_mesh_datas.evaluated_mesh_datas.values():
                LOG.debug(f"Register Mesh for later Evaluation : {mesh.object.name}")
                result.add_evaluated_mesh_data(mesh)

            ctx.task.evaluate_meshes.set_evaluate_meshes(result)
            return result


@dataclass(slots=True, frozen=True)
class EvaluateMeshesTask(Task):
    evaluated_mesh_datas: EvaluatedMeshDatas
    evaluate_meshes: EvaluateMeshes = EvaluateMeshes()
    producer: StoreEvaluateMeshes = StoreEvaluateMeshes()
    id: str = "EVALUATE_MESHES"

    def __repr__(self) -> str:
        result = f"{self.id}"
        return result

    def notify_finished(self, time_elapsed: float) -> None:
        with LOG.scope(LOG_SCOPE):
            LOG.info(
                message=f"{self.producer.name} succeeded",
                category=EventCategory.EVALUATE_MESHES,
                scope_state=ScopeState.EXIT,
                scope_duration=time_elapsed,
                data={
                    "status": BakeStatus.SUCCESS,
                },
            )

    def notify_failed(self, time_elapsed: float, error: str) -> None:
        with LOG.scope(LOG_SCOPE):
            LOG.error(
                message=f"{self.producer.name} failed",
                category=EventCategory.EVALUATE_MESHES,
                scope_state=ScopeState.EXIT,
                scope_duration=time_elapsed,
                data={
                    "status": BakeStatus.FAIL,
                },
            )
            LOG.error(
                message=error,
                category=EventCategory.EVALUATE_MESHES,
                data={
                    "status": BakeStatus.FAIL,
                },
            )
