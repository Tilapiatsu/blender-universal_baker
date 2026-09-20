from __future__ import annotations

import bpy
from mathutils import Vector

from universal_baker.constant import LOG


class ObjectOffset:
    def __init__(self, objects: list[bpy.types.Object], distance: tuple[float, float, float]) -> None:
        self.object_names = [o.name for o in objects]
        self.distance = distance

    @property
    def objects(self):
        return [bpy.data.objects.get(name) for name in self.object_names if bpy.data.objects.get(name) is not None]

    def offset(self):
        for obj in self.objects:
            LOG.debug(f"Offsetting object {obj.name}")
            obj.location += Vector(self.distance)

    def revert(self):
        for obj in self.objects:
            LOG.debug(f"Reverting object {obj.name} Position")
            obj.location -= Vector(self.distance)

    def __enter__(self):
        return self.offset()

    def __exit__(self, exc_type, exc_value, traceback):
        self.revert()
