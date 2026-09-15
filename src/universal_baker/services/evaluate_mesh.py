from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import bpy
from mathutils import Euler, Vector

from ..constant import LOG

LOG_SCOPE = "Evaluate"


@dataclass(slots=True, frozen=True)
class TransformState:
    location: Vector
    rotation_euler: Euler
    scale: Vector


class Evaluate(ABC):
    obj: bpy.types.Object

    @property
    @abstractmethod
    def needs_evaluation(self) -> bool:
        # TODO: Need to improve to take only the modifier that can modify the UVs later
        # GEOMETRY_MODIFIERS = {
        # 'SUBSURF',
        # 'BOOLEAN',
        # 'MIRROR',
        # 'NODES',
        # 'MASK',
        # 'DECIMATE',
        # ...
        # }
        return self.obj.data.users > 1 or len(self.obj.modifiers) > 0

    def __enter__(self): ...

    def __exit__(self, exc_type, exc_value, traceback): ...


class EvaluateMesh(Evaluate):
    def __init__(
        self,
        obj: bpy.types.Object,
    ):
        self.obj = obj
        self.evaluated_obj = None
        self.mesh = None

    @property
    def needs_evaluation(self) -> bool:
        return super().needs_evaluation

    def __enter__(self):
        if self.needs_evaluation:
            with LOG.scope(LOG_SCOPE):
                LOG.debug(f"Evaluate Object {self.obj.name}")
                depsgraph = bpy.context.evaluated_depsgraph_get()

                self.evaluated_obj = self.obj.evaluated_get(depsgraph)

                self.mesh = self.evaluated_obj.to_mesh()
        else:
            self.mesh = self.obj.data

        return self.mesh

    def __exit__(self, exc_type, exc_value, traceback):
        with LOG.scope(LOG_SCOPE):
            if self.evaluated_obj is not None:
                LOG.debug(f"Clean Evaluated Object : {self.evaluated_obj.name}")
                self.evaluated_obj.to_mesh_clear()


class EvaluateObject(Evaluate):
    def __init__(
        self,
        obj: bpy.types.Object | None,
    ):
        self.obj = obj
        self.evaluated_obj = None
        self.evaluated_mesh = None
        self.mesh = None

        if self.obj is None:
            return

        self.transform_state = TransformState(
            location=self.obj.location,
            rotation_euler=self.obj.rotation_euler,
            scale=self.obj.scale,
        )

    @property
    def needs_evaluation(self) -> bool:
        return super().needs_evaluation

    def evaluate(self) -> bpy.types.Object | None:
        if self.obj is None:
            return

        if self.needs_evaluation:
            with LOG.scope(LOG_SCOPE):
                LOG.debug(f"Evaluate Object {self.obj.name}")
                depsgraph = bpy.context.evaluated_depsgraph_get()

                self.evaluated_mesh = self.obj.evaluated_get(depsgraph)
                self.mesh = bpy.data.meshes.new_from_object(self.evaluated_mesh)
                self.evaluated_obj = bpy.data.objects.new(name=f"{self.obj.name}_UBK_EVALUATED", object_data=self.mesh)

                self.evaluated_obj.location = self.transform_state.location
                self.evaluated_obj.rotation_euler = self.transform_state.rotation_euler
                self.evaluated_obj.scale = self.transform_state.scale

        else:
            self.evaluated_obj = self.obj

        return self.evaluated_obj

    def clean(self) -> bool:
        if self.obj is None:
            return False

        with LOG.scope(LOG_SCOPE):
            if self.evaluated_obj is not None and self.evaluated_obj != self.obj:
                LOG.debug(f"Clean Evaluated Object : {self.evaluated_obj.name}")
                if self.evaluated_obj.name in bpy.data.objects:
                    bpy.data.objects.remove(self.evaluated_obj)

                if self.evaluated_mesh is not None and self.evaluated_mesh.name in bpy.data.meshes:
                    LOG.debug(f"Clean Evaluated Mesh: {self.evaluated_mesh.name}")
                    bpy.data.meshes.remove(self.evaluated_mesh)

                return True

            return False

    def __enter__(self) -> bpy.types.Object | None:
        return self.evaluate()

    def __exit__(self, exc_type, exc_value, traceback):
        self.clean()
