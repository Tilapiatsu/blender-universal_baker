from __future__ import annotations

import bpy

from ..constant import LOG

LOG_SCOPE = "Evaluate Mesh"


class EvaluateMesh:
    def __init__(
        self,
        obj: bpy.types.Object,
    ):
        self.obj = obj
        self.evaluated_obj = None
        self.mesh = None

    @property
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
