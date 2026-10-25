from __future__ import annotations

import bpy

from ..constant import CAGE_SKEW_REMESHER_ASSET_PATH, LOG
from ..properties.object import UBK_TargetObject
from ..properties.settings_cage import UBK_CageSettings
from ..resources.asset_external import AssetExtrenal
from ..runtime.asset_setup import AssetSetup
from ..runtime.bake_objects import BakeObjects
from ..services.asset_external_setup import AssetExternalCageSkewRemesherSetup
from .cage_object import CageObjectService
from .cage_skew import CustomCagePair
from .evaluate_mesh import EvaluateObject
from .visibility_override import VisibilityOverride


class ScenePrepare:
    target_objects: list[UBK_TargetObject]
    bake_objects: dict[str, BakeObjects]
    evaluate_objects: dict[str, EvaluateObject]
    evaluate_cages: dict[str, EvaluateObject]
    visibility_override: list[VisibilityOverride]
    temporary_objects: list[bpy.types.Object]
    asset_setups: list[AssetSetup]

    def __init__(self) -> None:
        self.target_objects: list[UBK_TargetObject] = []
        self.bake_objects: dict[str, BakeObjects] = {}
        self.evaluate_objects: dict[str, EvaluateObject] = {}
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

            if obj.have_source:
                if obj.settings_cage.cage_object is None:
                    message = "Cage Object Missing"
                    LOG.critical(message)
                    raise RuntimeError(message)
                    return

                cage = obj.settings_cage.cage_object

                if obj.settings_cage.is_cage_generated:
                    cage = CageObjectService.acquire(obj)
                    if obj.settings_cage.is_skew_correction_enabled:
                        evaluate_obj = EvaluateObject(obj.target_skew)
                        self.evaluate_objects[obj.uuid] = evaluate_obj
                        evaluated_obj = evaluate_obj.evaluate()
                        cage = self._evaluate_cage(obj)

                    else:
                        evaluated_obj = self._evaluate_object(obj)

                # Custom Cage
                elif obj.settings_cage.cage_object is not None:
                    evaluated_obj = self._evaluate_object(obj)
                    cage = self._evaluate_cage(obj)

                assert cage is not None

                vo = VisibilityOverride(cage, render=False)
                vo.set_visibility()
                self.visibility_override.append(vo)

            else:
                evaluated_obj = self._evaluate_object(obj)
                cage = None

            bake_object = BakeObjects(
                target_object=evaluated_obj,
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

    def _evaluate_object(self, obj: UBK_TargetObject) -> bpy.types.Object:
        evaluate_obj = EvaluateObject(obj.object)
        self.evaluate_objects[obj.uuid] = evaluate_obj
        return evaluate_obj.evaluate()

    def _evaluate_cage(self, obj: UBK_TargetObject) -> bpy.types.Object:
        evaluate_cage = EvaluateObject(obj.settings_cage.cage_object)
        self.evaluate_cages[obj.uuid] = evaluate_cage
        return evaluate_cage.evaluate()

    def __exit__(self, exc_type, exc_value, traceback):
        LOG.debug("Clean Scene Preparation")
        for vo in self.visibility_override:
            vo.revert_visibility()

        for uuid, o in self.evaluate_objects.items():
            bake_object = self.bake_objects.get(uuid)
            if bake_object is not None:
                if not bake_object.is_cage_generated:
                    continue

                cage = bake_object.cage_object

                if cage is not None:
                    LOG.debug(f"Clean Cage Object {cage.name}")
                    bpy.data.objects.remove(cage)

            o.clean()

        for uuid, o in self.evaluate_cages.items():
            o.clean()

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
