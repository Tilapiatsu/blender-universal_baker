from __future__ import annotations

import bpy

from ..constant import LOG
from ..properties.object import UBK_TargetObject
from ..runtime.bake_objects import BakeObjects
from ..services.cage_object import CageObjectService
from ..services.evaluate_mesh import EvaluateObject


class ScenePrepare:
    target_objects: list[UBK_TargetObject]
    bake_objects: dict[str, BakeObjects]
    evaluate_objects: dict[str, EvaluateObject]
    evaluated_cages: dict[str, EvaluateObject]

    def __init__(self) -> None:
        self.target_objects = []
        self.bake_objects = {}
        self.evaluate_objects = {}
        self.evaluated_cages = {}

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

            cage_hidden = False
            if obj.have_source:
                if obj.settings_cage.cage_object is None:
                    message = "Cage Object Missing"
                    LOG.critical(message)
                    raise RuntimeError(message)
                    return

                cage = obj.settings_cage.cage_object

                if obj.settings_cage.is_cage_generated:
                    cage = CageObjectService.acquire(evaluated_obj, obj.settings_cage)

                elif obj.settings_cage.cage_object is not None:
                    evaluate_cage = EvaluateObject(obj.settings_cage.cage_object)

                    self.evaluated_cages[obj.uuid] = evaluate_cage

                    cage = evaluate_cage.evaluate()

                assert cage is not None

                cage_hidden = cage.hide_render
                cage.hide_render = True
            else:
                cage = None

            bake_object = BakeObjects(
                target_object=evaluated_obj,
                cage_object=cage,
                cage_hidden=cage_hidden,
                is_cage_generated=obj.settings_cage.is_cage_generated,
                source_objects=source_objects,
            )

            if obj.have_source:
                if bake_object.is_valid:
                    LOG.info(f"Target Object {obj.object.name} is valid")
                else:
                    assert cage is not None
                    message = f"{bake_object.target_object.name} Object and {cage.name} cage topology doesn't match"
                    LOG.critical(message)
                    LOG.debug(f"{obj.object.name} vert count : {len(obj.object.data.vertices)}")
                    LOG.debug(
                        f"{obj.settings_cage.cage_object.name} vert count : {len(obj.settings_cage.cage_object.data.vertices)}"
                    )
                    LOG.debug(
                        f"{bake_object.target_object.name} vert count : {len(bake_object.target_object.data.vertices)}"
                    )
                    LOG.debug(f"{cage.name} vert count : {len(cage.data.vertices)}")
                    raise RuntimeError(message)

            self.bake_objects[obj.uuid] = bake_object

        return self.bake_objects

    def __exit__(self, exc_type, exc_value, traceback):
        LOG.debug("Clean Scene Preparation")
        for uuid, o in self.evaluate_objects.items():
            bake_object = self.bake_objects.get(uuid)
            if bake_object is not None:
                if not bake_object.is_cage_generated:
                    if bake_object.cage_object is not None:
                        bake_object.cage_object.hide_render = bake_object.cage_hidden
                    continue

                cage = bake_object.cage_object

                if cage is not None:
                    LOG.debug(f"Clean Cage Object {cage.name}")
                    bpy.data.objects.remove(cage)

            o.clean()

        for uuid, o in self.evaluated_cages.items():
            o.clean()
