from __future__ import annotations

import bpy


class EvaluatedMeshContext:
    def __init__(
        self,
        obj: bpy.types.Object,
        depsgraph: bpy.types.Depsgraph,
    ):
        self.obj = obj
        self.depsgraph = depsgraph
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
            self.evaluated_obj = self.obj.evaluated_get(self.depsgraph)
            self.mesh = self.evaluated_obj.to_mesh()
        else:
            self.mesh = self.obj.data

        return self.mesh

    def __exit__(self, exc_type, exc_value, traceback):
        if self.evaluated_obj is not None:
            self.evaluated_obj.to_mesh_clear()
