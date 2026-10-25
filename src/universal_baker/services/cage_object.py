from __future__ import annotations

from dataclasses import dataclass

import bpy
from universal_baker.parameter.parameter_applier import ParameterApplier
from universal_baker.parameter.parameter_context import ParameterContext
from universal_baker.services.parameter_service import ParameterService

from ..constant import CAGE_SKEW_REMESHER_ASSET_PATH, LOG, OFFSET_VERTEX_GROUP_NAME
from ..core.registry_definition import registry_definition
from ..properties.object import UBK_TargetObject
from ..properties.settings_cage import UBK_CageSettings
from ..resources.asset_external import AssetExtrenal
from ..resources.asset_info import CageSkewInfo
from .asset_external_setup import AssetExternalCageSkewRemesherSetup

LOG_SCOPE = "Cage Object"


@dataclass(slots=True)
class CageObject:
    object: bpy.types.Object
    collection: bpy.types.Collection | None
    owns_collection: bool


class CageObjectService:
    """Service to create and manage generated cage objects"""

    CAGE_SUFFIX = "UBK_CAGE"
    SKEW_TARGET_SUFFIX = "UBK_SKEW_TARGET"
    MODIFIER_NAME = "UBK_CAGE"
    MODIFIER_TYPE = "NODES"
    NODE_GROUP_NAME = "GN_ResamplePaint"

    @classmethod
    def acquire(cls, target: UBK_TargetObject) -> bpy.types.Object:
        with LOG.scope(LOG_SCOPE):
            LOG.debug(f"Acquire Cage Object for {target.object.name}")

            settings_cage: UBK_CageSettings = target.settings_cage

            cage = None

            if not settings_cage.is_cage_generated:
                return settings_cage.cage_object_custom
            else:
                if settings_cage.cage_object_generated is not None and len(target.object.data.vertices) == len(
                    settings_cage.cage_object_generated.data.vertices
                ):
                    LOG.debug("Retrieve Generated Cage")
                    cls._ensure_modifiers(target, settings_cage)
                    cls._ensure_cage_transform(settings_cage.cage_object_generated, target.object)
                    cage = settings_cage.cage_object_generated
                else:
                    LOG.debug("Generated new Cage")
                    cage = cls._get_or_create_cage(target)
                    cls._ensure_cage_transform(cage, target.object)
                    settings_cage.cage_object_generated = cage

                if settings_cage.is_skew_correction_enabled:
                    LOG.debug("Ensure Skew Target")
                    cls._ensure_skew_target(target)

            return cage

    @staticmethod
    def _ensure_cage_transform(cage: bpy.types.Object, target: bpy.types.Object) -> None:
        cage.location = target.location
        cage.rotation_euler = target.rotation_euler
        cage.scale = target.scale

    @classmethod
    def _get_or_create_cage(cls, target: UBK_TargetObject) -> bpy.types.Object:
        cage_name = cls._get_cage_name(target.object.name)
        cage = bpy.data.objects.get(cage_name)

        if cage is not None and cage.data == target.object.data:
            cls._ensure_modifiers(target, cage)
        else:
            cage = target.object.copy()
            cage.name = cage_name
            cls._ensure_modifiers(target, cage)

        return cage

    @classmethod
    def _ensure_skew_target(cls, target: UBK_TargetObject):
        skew_target_name = cls._get_skew_target_name(target.object.name)
        skew_target = bpy.data.objects.get(skew_target_name)

        if skew_target is not None and skew_target.data == target.target_skew.data:
            cls._ensure_modifiers(target, skew_target)
            return skew_target

        skew_target = target.object.copy()
        skew_target.name = skew_target_name

        cls._ensure_modifiers(target, skew_target)
        return skew_target

    @classmethod
    def _ensure_modifiers(
        cls,
        target: UBK_TargetObject,
        obj: bpy.types.Object,
    ) -> bpy.types.Modifier:
        cls._ensure_vertex_group(target.object)

        modifier = None

        for m in obj.modifiers:
            if m.type == cls.MODIFIER_TYPE and m.name == cls.MODIFIER_NAME and m.node_group.name == cls.NODE_GROUP_NAME:
                modifier = m
                break

        if modifier is None:
            asset = AssetExtrenal(filepath=CAGE_SKEW_REMESHER_ASSET_PATH)
            setup = AssetExternalCageSkewRemesherSetup.prepare(
                asset_remesher=asset,
                target_object=obj,
                uv_map=target.uv_layer,
                skew_image=target.settings_cage.skew_image,
                precision=target.settings_cage.skew_precision,
                offset=target.settings_cage.cage_extrusion,
            )
            target.target_skew = setup.target
            target.settings_cage.cage_object_generated = setup.cage
            # setup.cleanup()

            return modifier

        cls._apply_modifier_parameters(target)

        return modifier

    @classmethod
    def _ensure_vertex_group(cls, cage: bpy.types.Object) -> None:
        vertex_group = cage.vertex_groups.get(OFFSET_VERTEX_GROUP_NAME)

        if vertex_group is None:
            vertex_group = cage.vertex_groups.new(name=OFFSET_VERTEX_GROUP_NAME)
            vertex_group.add([0], 0.0, "REPLACE")

    @classmethod
    def _get_cage_name(cls, target_name: str) -> str:
        return f"{target_name}_{cls.CAGE_SUFFIX}"

    @classmethod
    def _get_skew_target_name(cls, target_name: str) -> str:
        return f"{target_name}_{cls.SKEW_TARGET_SUFFIX}"

    @classmethod
    def _apply_modifier_parameters(
        cls,
        target: UBK_TargetObject,
    ):
        definition = registry_definition.get_custom("SKEW_REMESHER")
        if definition is None:
            LOG.error("Parameter definition not found")
            return

        if target.target_skew is not None:
            # NOTE: Applying to Target
            target_info = cls._get_cage_skew_info(
                target.uv_layer,
                target.settings_cage.skew_image,
                target.settings_cage.skew_precision,
                0,
            )
            snapshot = ParameterService.snapshot_asset(definition, target_info)

            LOG.debug("Applying Target Skew parameters")

            parameter_context = ParameterContext(
                object=target.target_skew,
                scene=bpy.context.scene,
            )

            ParameterApplier.apply(
                definition,
                snapshot,
                parameter_context,
            )

        if target.settings_cage.cage_object_generated is not None:
            # NOTE: Applying to Cage
            cage_info = cls._get_cage_skew_info(
                target.uv_layer,
                target.settings_cage.skew_image,
                target.settings_cage.skew_precision,
                target.settings_cage.offset,
            )
            snapshot = ParameterService.snapshot_asset(definition, cage_info)

            LOG.debug("Applying Target Skew parameters")

            parameter_context = ParameterContext(
                object=target.settings_cage.cage_object_generated,
                scene=bpy.context.scene,
            )

            ParameterApplier.apply(
                definition,
                snapshot,
                parameter_context,
            )

    @classmethod
    def _get_cage_skew_info(
        cls,
        uv_map: str,
        image: bpy.types.Image,
        precision: float,
        offset: float,
        optimize_resample: bool = True,
    ) -> CageSkewInfo:
        cage_info = CageSkewInfo(
            uvmap=uv_map,
            skew_image=image,
            precision=precision,
            offset=offset,
            offset_group=OFFSET_VERTEX_GROUP_NAME,
            optimize_resample=optimize_resample,
        )
        return cage_info
