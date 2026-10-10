from __future__ import annotations

from abc import ABC, abstractmethod

import bpy

from ..constant import LOG
from ..services.visibility_override import VisibilityOverride

LOG_SCOPE = "Evaluate"


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
        self.has_been_evaluated: bool = False

        if self.obj is None:
            return

        self.visibility_override = VisibilityOverride(self.obj, render=False, viewport=True)

    @property
    def needs_evaluation(self) -> bool:
        return super().needs_evaluation

    def evaluate(self) -> bpy.types.Object | None:
        if self.obj is None:
            return

        if self.needs_evaluation:
            self.visibility_override.set_visibility()
            with LOG.scope(LOG_SCOPE):
                LOG.debug(f"Evaluate Object {self.obj.name}")
                depsgraph = bpy.context.evaluated_depsgraph_get()

                self.evaluated_mesh = self.obj.evaluated_get(depsgraph)
                self.mesh = bpy.data.meshes.new_from_object(self.evaluated_mesh)
                self.evaluated_obj = bpy.data.objects.new(name=f"{self.obj.name}_UBK_EVALUATED", object_data=self.mesh)

                self.evaluated_obj.matrix_world = self.obj.matrix_world.copy()

                self.has_been_evaluated = True

        else:
            self.evaluated_obj = self.obj

        return self.evaluated_obj

    def clean(self) -> bool:
        if self.obj is None:
            return False

        with LOG.scope(LOG_SCOPE):
            if self.has_been_evaluated:
                self.visibility_override.revert_visibility()
                if self.evaluated_obj is not None and self.evaluated_obj.name in bpy.data.objects:
                    LOG.debug(f"Clean Evaluated Object : {self.evaluated_obj.name}")
                    bpy.data.objects.remove(self.evaluated_obj)

                if self.mesh is not None and self.mesh.name in bpy.data.meshes:
                    LOG.debug(f"Clean Evaluated Mesh : {self.mesh.name}")
                    bpy.data.meshes.remove(self.mesh)

                return True

            return False

    def __enter__(self) -> bpy.types.Object | None:
        return self.evaluate()

    def __exit__(self, exc_type, exc_value, traceback):
        self.clean()
