from __future__ import annotations

import bpy

from ..constant import LOG
from ..properties.object import UBK_TargetObject
from ..properties.settings_cage import UBK_CageSettings
from ..runtime.asset_setup import AssetSetup
from ..runtime.bake_objects import BakeObjects
from .cage_skew import CustomCagePair
from .evaluate_mesh import EvaluateObject
from .visibility_override import VisibilityOverride


class ScenePrepare:
    target_objects: list[UBK_TargetObject]
    bake_objects: dict[str, BakeObjects]
    evaluate_targets: dict[str, EvaluateObject]
    evaluate_cages: dict[str, EvaluateObject]
    visibility_override: list[VisibilityOverride]
    temporary_objects: list[bpy.types.Object]
    asset_setups: list[AssetSetup]

    def __init__(self) -> None:
        self.target_objects: list[UBK_TargetObject] = []
        self.bake_objects: dict[str, BakeObjects] = {}
        self.evaluate_targets: dict[str, EvaluateObject] = {}
        self.evaluate_cages: dict[str, EvaluateObject] = {}
        self.visibility_override: list[VisibilityOverride] = []
        self.asset_setups: list[AssetSetup] = []

    def add_target_object(self, target_object: UBK_TargetObject):
        self.target_objects.append(target_object)

    def __enter__(self) -> dict[str, BakeObjects]:
        for obj in self.target_objects:
            if not obj.enabled or obj.object is None:
                continue

            LOG.debug(f"Prepare Object {obj.object.name}")

            source_objects = [s.object for s in obj.source_objects if s.enabled and s.object is not None]

            for s in source_objects:
                # NOTE: Set source object invisible to camera
                vo = VisibilityOverride(
                    s,
                    render=True,
                    visible_camera=False,
                    visible_diffuse=True,
                    visible_glossy=True,
                    visible_transmission=True,
                    visible_volume_scatter=True,
                    visible_shadow=True,
                )
                vo.set_visibility()
                self.visibility_override.append(vo)

            target = obj.target_object
            obj.ensure_cage_object()
            cage = obj.settings_cage.cage_object

            if obj.have_source:
                if cage is None:
                    message = "Cage Object Missing"
                    LOG.critical(message)
                    raise RuntimeError(message)
                    return

                vo = VisibilityOverride(cage, render=False)
                vo.set_visibility()
                self.visibility_override.append(vo)

            target = self._evaluate_target(target, obj.uuid)
            cage = self._evaluate_cage(cage, obj.uuid)

            bake_object = BakeObjects(
                target_object=target,
                cage_object=cage,
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

    def _evaluate_target(self, obj: bpy.types.Object, uuid: str) -> bpy.types.Object:
        evaluate_obj = EvaluateObject(obj)
        self.evaluate_targets[uuid] = evaluate_obj
        return evaluate_obj.evaluate()

    def _evaluate_cage(self, obj: bpy.types.Object, uuid: str) -> bpy.types.Object:
        evaluate_obj = EvaluateObject(obj)
        self.evaluate_cages[uuid] = evaluate_obj
        return evaluate_obj.evaluate()

    def __exit__(self, exc_type, exc_value, traceback):
        LOG.debug("Clean Scene Preparation")
        for vo in self.visibility_override:
            vo.revert_visibility()

        for o in self.evaluate_targets.values():
            o.cleanup()

        for o in self.evaluate_cages.values():
            o.cleanup()

        for s in self.asset_setups:
            s.cleanup()

    @classmethod
    def get_skew_cage(
        cls,
        obj: bpy.types.Object,
        settings_cage: UBK_CageSettings,
        uv_layer_name: str,
    ) -> CustomCagePair:
        from ..services.cage_skew import SkewCageBuilder

        service = SkewCageBuilder()

        return service.build(
            target_object=obj,
            cage_object=settings_cage.cage_object_generated,
            skew_image=settings_cage.skew_image,
            uv_layer_name=uv_layer_name,
            cage_extrusion=settings_cage.cage_extrusion,
        )
