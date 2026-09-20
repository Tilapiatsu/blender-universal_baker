from __future__ import annotations

from contextlib import contextmanager

import bpy

from ..constant import CAGE_SCENE_OFFSET, LOG
from ..core.registry_definition import registry_definition
from ..parameter.parameter_applier import ParameterApplier
from ..parameter.parameter_context import ParameterContext
from ..resources.asset_external import AssetExtrenal
from ..resources.asset_info import CageInfo
from ..runtime.asset_setup import AssetSetup
from ..runtime.bake_objects import BakeObjects
from ..services.bake_material import BakeMaterialService
from ..services.object_offset import ObjectOffset
from ..services.parameter_service import ParameterService
from .asset_external import AssetExternalService

LOG_SCOPE = "External Asset Setup Service"


class ExternalAssetSetupError(RuntimeError):
    pass


class AssetExternalSetupBase:
    @classmethod
    def _prepare_object(
        cls,
        obj: bpy.types.Object,
        prototype: bpy.types.Object,
        setup: AssetSetup,
    ) -> bpy.types.Object:
        LOG.debug(f"Prepare setup for {obj.name}")
        duplicate = cls._duplicate_object(obj)

        setup.temporary_objects.append(duplicate)

        cls._copy_material(prototype, duplicate, setup)
        cls._copy_modifiers(prototype, duplicate)

        return duplicate

    @contextmanager
    @staticmethod
    def get_prototype_material(asset: AssetExtrenal) -> bpy.types.Material:
        prototype = AssetExternalService.load_prototype(asset)
        copy = prototype.active_material.copy()

        copy.use_nodes = True

        try:
            yield copy
        finally:
            LOG.debug("Cleanup prototype material")
            bpy.data.materials.remove(copy)
            prototype_materials = [s.material for s in prototype.material_slots if s.material is not None]
            for m in prototype_materials:
                bpy.data.materials.remove(m)

            bpy.data.objects.remove(prototype)

    @staticmethod
    def _duplicate_object(obj: bpy.types.Object, instance: bool = False) -> bpy.types.Object:
        LOG.debug(f"Duplicate object {obj.name}")
        bake_object = obj.copy()

        if obj.data is not None and not instance:
            bake_object.data = obj.data.copy()

        bake_object.name = f"UBK_TMP_{obj.name}"

        # Link it to the same collection as the target.
        for collection in obj.users_collection:
            collection.objects.link(bake_object)

        return bake_object

    @staticmethod
    def _copy_material(prototype: bpy.types.Object, obj: bpy.types.Object, setup: AssetSetup) -> None:
        material = prototype.active_material

        if material is None:
            raise ExternalAssetSetupError("Custom baker prototype does not have an active material.")

        material_copy = material.copy()

        material_copy.name = f"UBK_TMP_{material.name}"

        LOG.debug(f"Assign {material_copy.name} to {obj.name}")
        obj.data.materials.clear()
        obj.data.materials.append(material_copy)

        setup.temporary_materials.append(material_copy)

    @classmethod
    def _copy_modifiers(cls, prototype: bpy.types.Object, obj: bpy.types.Object) -> None:
        for source_modifier in prototype.modifiers:
            LOG.debug(f"Copying modifier {source_modifier.name} to {obj.name}")
            modifier = obj.modifiers.new(
                name=source_modifier.name,
                type=source_modifier.type,
            )

            cls._copy_rna_properties(
                source_modifier,
                modifier,
            )

    @staticmethod
    def _copy_rna_properties(source, destination) -> None:
        for prop in source.bl_rna.properties:
            identifier = prop.identifier

            if identifier in {"rna_type", "name", "type"}:
                continue

            if prop.is_readonly:
                continue

            try:
                setattr(
                    destination,
                    identifier,
                    getattr(
                        source,
                        identifier,
                    ),
                )

            except (AttributeError, TypeError, ValueError):
                # Some RNA properties cannot be copied
                # generically. Ignore them for the MVP.
                continue

    @staticmethod
    def _remove_object(obj: bpy.types.Object | None) -> None:
        if obj is None:
            return

        try:
            bpy.data.objects.remove(
                obj,
                do_unlink=True,
            )
        except (ReferenceError, RuntimeError):
            pass


class AssetExternalBakeSetup(AssetExternalSetupBase):
    """Apply the External asset to the proper bake objects"""

    @classmethod
    def prepare(cls, asset: AssetExtrenal, bake_objects: BakeObjects) -> AssetSetup:
        with LOG.scope(LOG_SCOPE):
            prototype = AssetExternalService.load_prototype(asset)

            setup = AssetSetup()
            setup.temporary_objects.append(prototype)
            proto_materials = [s.material for s in prototype.material_slots if s.material is not None]
            for m in proto_materials:
                LOG.debug(f"store prototype material : {m.name}")
                setup.temporary_materials.append(m)

            try:
                if bake_objects.selected_to_active:
                    duplicated_sources = []
                    for o in bake_objects.source_objects:
                        duplicated_source = cls._prepare_object(o, prototype, setup)
                        duplicated_sources.append(duplicated_source)

                    setup.sources = duplicated_sources
                    setup.target = bake_objects.target_object
                    material_setup = BakeMaterialService.prepare(
                        targets=[bake_objects.target_object], sources=duplicated_sources
                    )
                    setup.material_setup = material_setup
                    setup.cage = bake_objects.cage_object

                else:
                    material_setup = BakeMaterialService.prepare(targets=[bake_objects.target_object], sources=[])
                    setup.material_setup = material_setup
                    setup.target = cls._prepare_object(bake_objects.target_object, prototype, setup)

                bake_objects.target_object.hide_render = True

                return setup

            except Exception:
                LOG.error("Preparation Failed")
                setup.cleanup()

                # The prototype itself was appended from the
                # external blend and must also be removed.
                cls._remove_object(prototype)
                raise RuntimeError


class AssetExternalCageSetup(AssetExternalSetupBase):
    """Apply the External asset to the proper bake objects"""

    @classmethod
    def prepare(cls, asset: AssetExtrenal, bake_objects: BakeObjects, uv_map: str) -> AssetSetup:
        with LOG.scope(LOG_SCOPE):
            prototype = AssetExternalService.load_prototype(asset)

            setup = AssetSetup()
            setup.temporary_objects.append(prototype)
            proto_materials = [s.material for s in prototype.material_slots if s.material is not None]
            for m in proto_materials:
                LOG.debug(f"store prototype material : {m.name}")
                setup.temporary_materials.append(m)

            try:
                projection_cage = cls._prepare_projection_cage(bake_objects.cage_object, setup)

                setup.sources = bake_objects.source_objects
                setup.target = bake_objects.target_object
                setup.projection_cage = projection_cage

                setup.projection_target = cls._prepare_projection_target(bake_objects.target_object, prototype, setup)
                setup.cage = bake_objects.cage_object

                offset_objects = bake_objects.source_objects + [
                    projection_cage,
                    bake_objects.target_object,
                ]

                do_not_offset_objects = [setup.projection_target, setup.cage]

                objects = list(bpy.context.scene.objects) + [setup.projection_cage]

                offset_objects = [o for o in objects if o not in do_not_offset_objects]

                offset = (0, CAGE_SCENE_OFFSET, CAGE_SCENE_OFFSET)

                setup.object_offset = cls._offset_objects(offset_objects, offset)

                cls._apply_cage_parameters(setup, uv_map, offset)

                return setup

            except Exception:
                LOG.error("Preparation Failed")
                setup.cleanup()

                # The prototype itself was appended from the
                # external blend and must also be removed.
                cls._remove_object(prototype)
                raise RuntimeError

    @classmethod
    def _prepare_projection_cage(cls, obj: bpy.types.Object, setup: AssetSetup) -> bpy.types.Object:
        duplicate = cls._duplicate_object(obj, instance=True)
        duplicate.name += "_PROJECTION_CAGE"

        setup.temporary_objects.append(duplicate)

        duplicate.hide_viewport = True

        return duplicate

    @classmethod
    def _prepare_projection_target(
        cls, obj: bpy.types.Object, prototype: bpy.types.Object, setup: AssetSetup
    ) -> bpy.types.Object:
        duplicate = cls._prepare_object(obj, prototype, setup)
        duplicate.name += "_PROJECTION_TARGET"

        return duplicate

    @classmethod
    def _offset_objects(cls, objects: list[bpy.types.Object], distance: tuple[float, float, float]) -> ObjectOffset:
        offset = ObjectOffset(objects, distance)
        offset.offset()
        return offset

    @classmethod
    def _apply_cage_parameters(
        cls,
        setup: AssetSetup,
        uv_map: str,
        offset: tuple[float, float, float],
    ):
        definition = registry_definition.get_custom("BAKE_PREVIEW")
        if definition is None:
            LOG.error("Parameter definition not found")
            return

        cage_info = cls._get_cage_info(setup, uv_map, cls._negate_tuple(offset))
        snapshot = ParameterService.snapshot_asset(definition, cage_info)

        LOG.debug("Applying Cage parameters")

        parameter_context = ParameterContext(
            object=setup.projection_target,
            scene=bpy.context.scene,
        )

        ParameterApplier.apply(
            definition,
            snapshot,
            parameter_context,
        )

    @classmethod
    def _get_cage_info(
        cls,
        setup: AssetSetup,
        uv_map: str,
        offset: tuple[float, float, float],
    ):
        cage_info = CageInfo(
            cage_object=setup.projection_cage,
            target_object=setup.target,
            offset=offset,
            uvmap=uv_map,
        )
        return cage_info

    @classmethod
    def _negate_tuple(cls, t: tuple[float, float, float]) -> tuple[float, float, float]:
        return (t[0] * -1, t[1] * -1, t[2] * -1)
