from __future__ import annotations

from dataclasses import dataclass, field

import bpy

from ..constant import LOG
from ..properties.object import UBK_TargetObject
from ..services.evaluate_mesh import EvaluateMesh

LOG_SCOPE = "Evaluated Target"


@dataclass(slots=True)
class EvaluatedMeshData:
    uuid: str
    name: str
    object: bpy.types.Object
    mesh: bpy.types.Mesh


@dataclass(slots=True)
class EvaluatedMeshDatas:
    evaluated_mesh_datas: dict[str, EvaluatedMeshData] = field(default_factory=dict)

    def add_object(self, obj: UBK_TargetObject):
        with LOG.scope(LOG_SCOPE):
            if obj.object is None:
                LOG.error("Object is undefined")
                return

            if obj.object.type != "MESH":
                LOG.error("Object should be a Mesh")
                return

            self.evaluated_mesh_datas[obj.object.name] = EvaluatedMeshData(
                uuid=obj.uuid, name=obj.object.name, object=obj.object, mesh=obj.object.data
            )

    def set_evaluated_meshes(self, evaluated_meshes: EvaluatedMeshDatas):
        self.evaluated_mesh_datas = evaluated_meshes.evaluated_mesh_datas


class EvaluateMeshes:
    _evaluate_meshes: dict[str, EvaluateMesh]

    def __init__(self) -> None:
        self._evaluate_meshes = {}

    def add_evaluated_mesh_data(self, evaluated_mesh_data: EvaluatedMeshData):
        with LOG.scope(LOG_SCOPE):
            if evaluated_mesh_data.object is None:
                LOG.error("Object is undefined")
                return

            if evaluated_mesh_data.object.type != "MESH":
                LOG.error("Object should be a Mesh")
                return

        self._evaluate_meshes[evaluated_mesh_data.object.name] = EvaluateMesh(evaluated_mesh_data.object)

    def set_evaluate_meshes(self, evaluated_meshes: EvaluateMeshes):
        self._evaluate_meshes = evaluated_meshes._evaluate_meshes

    def __contains__(self, key: int) -> bool:
        return key in self._evaluate_meshes

    def keys(self):
        return list(self._evaluate_meshes.keys())

    def values(self):
        return list(self._evaluate_meshes.values())

    def update(self, *args, **kwargs):
        return self._evaluate_meshes.update(*args, **kwargs)

    def items(self):
        return self._evaluate_meshes.items()

    # def __setitem__(self, key: str, item: EvaluateMesh):
    #     self._evaluate_meshes[key] = item

    def __getitem__(self, key: str) -> EvaluateMesh:
        td = self._evaluate_meshes[key]
        return td

    def __repr__(self) -> str:
        return repr(self._evaluate_meshes)

    def __len__(self) -> int:
        return len(self._evaluate_meshes)

    def __delitem__(self, key: str) -> None:
        del self._evaluate_meshes[key]
