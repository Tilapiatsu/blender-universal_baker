from __future__ import annotations

import bpy

from dataclasses import dataclass

from ..constant import LOG
from ..properties.object import UBK_TargetObject

LOG_SCOPE = "Evaluated Target"


@dataclass(slots=True)
class EvaluatedMesh:
    uuid: str
    name: str
    object: bpy.types.Object
    mesh: bpy.types.Mesh


@dataclass(slots=True)
class EvaluatedMeshes:
    targets: dict[str, EvaluatedMesh]

    def add_target(self, obj: UBK_TargetObject):
        with LOG.scope(LOG_SCOPE):
            if obj.object is None:
                LOG.error("Object is undefined")
                return

            if obj.object.type != "MESH":
                LOG.error("Object should be a Mesh")
                return

            self.targets[obj.object.name] = EvaluatedMesh(
                uuid=obj.uuid, name=obj.object.name, object=obj.object, mesh=obj.object.data
            )
