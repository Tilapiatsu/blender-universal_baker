from __future__ import annotations

from dataclasses import dataclass, field

import bpy

from ..constant import LOG
from ..properties.object import UBK_TargetObject
from ..services.cage_object import CageObjectService
from ..services.evaluate_mesh import EvaluateObject


@dataclass(slots=True, frozen=True)
class BakeObjects:
    target_object: bpy.types.Object
    cage_object: bpy.types.Object | None
    source_objects: list[bpy.types.Object] = field(default_factory=list)

    @property
    def selected_to_active(self) -> bool:
        return len(self.source_objects) > 0 if self.source_objects is not None else False

    @property
    def baker_material_objects(self) -> list[bpy.types.Object]:
        if self.selected_to_active:
            return self.source_objects
        else:
            return [self.target_object]


class ScenePrepare:
    target_objects: list[UBK_TargetObject]
    bake_objects: dict[str, BakeObjects]
    evaluate_objects: dict[str, EvaluateObject]

    def __init__(self) -> None:
        self.target_objects = []
        self.bake_objects = {}
        self.evaluate_objects = {}

    def add_target_object(self, target_object: UBK_TargetObject):
        self.target_objects.append(target_object)

    def __enter__(self) -> dict[str, BakeObjects]:
        for obj in self.target_objects:
            if not obj.enabled or obj.object is None:
                continue

            LOG.debug(f"Prepare Object {obj.object.name}")

            source_objects = [s.object for s in obj.source_objects if s.enabled and s.object is not None]

            evaluate_obj = EvaluateObject(obj.object)
            self.evaluate_objects[obj.uuid] = evaluate_obj

            evaluated_obj = evaluate_obj.evaluate()

            cage = CageObjectService.acquire(evaluated_obj, obj.settings_cage)

            bake_object = BakeObjects(
                target_object=evaluated_obj,
                cage_object=cage,
                source_objects=source_objects,
            )

            self.bake_objects[obj.uuid] = bake_object

        return self.bake_objects

    def __exit__(self, exc_type, exc_value, traceback):
        LOG.debug("Clean Scene Preparation")
        for uuid, o in self.evaluate_objects.items():
            if o.clean():
                bake_object = self.bake_objects.get(uuid)
                if bake_object is None:
                    continue

                cage = bake_object.cage_object

                if cage is None:
                    continue

                LOG.debug(f"Clean Cage Object {cage.name}")
                bpy.data.objects.remove(cage)
