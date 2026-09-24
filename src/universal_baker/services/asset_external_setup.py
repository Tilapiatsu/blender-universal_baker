from __future__ import annotations

from contextlib import contextmanager

import bpy

from ..constant import CAGE_SCENE_OFFSET, LOG
from ..core.registry_definition import registry_definition
from ..parameter.parameter_applier import ParameterApplier
from ..parameter.parameter_context import ParameterContext
from ..resources.asset_external import AssetExtrenal
from ..resources.asset_info import CageInfo, SourcesInfo
from ..runtime.asset_setup import AssetSetup
from ..runtime.bake_objects import BakeObjects
from ..services.bake_material import BakeMaterialService
from ..services.object_offset import ObjectOffset
from ..services.parameter_service import ParameterService
from ..services.shader_node_insert import ShaderNodeInsert
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
    def get_prototype_node(asset: AssetExtrenal, node_name: str) -> bpy.types.Node:
        with bpy.data.libraries.load(str(asset.filepath), link=False) as (data_from, data_to):
            if node_name in data_from.node_groups:
                data_to.node_groups.append(node_name)

        appended_node = bpy.data.node_groups.get(node_name)

        return appended_node

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
    def prepare(
        cls,
        asset_portal: AssetExtrenal,
        asset_clipping: AssetExtrenal,
        bake_objects: BakeObjects,
        uv_map: str,
        max_ray_distance: float,
    ) -> AssetSetup:
        with LOG.scope(LOG_SCOPE):
            prototype_portal = AssetExternalService.load_prototype(asset_portal)
            prototype_clipping = AssetExternalService.load_prototype(asset_clipping)

            setup = AssetSetup()

            setup.temporary_objects.append(prototype_portal)
            setup.temporary_objects.append(prototype_clipping)

            proto_materials = [s.material for s in prototype_portal.material_slots if s.material is not None]
            proto_materials += [s.material for s in prototype_clipping.material_slots if s.material is not None]

            for m in proto_materials:
                LOG.debug(f"store prototype material : {m.name}")
                setup.temporary_materials.append(m)

            try:
                projection_cage = cls._prepare_projection_cage(bake_objects.cage_object, setup)

                setup.sources = bake_objects.source_objects
                setup.target = bake_objects.target_object
                setup.projection_cage = projection_cage

                setup.projection_target = cls._prepare_projection_target(
                    bake_objects.target_object, prototype_portal, setup
                )
                setup.cage = bake_objects.cage_object

                objects = list(bpy.context.scene.objects) + [setup.projection_cage]

                do_not_offset_objects_edit = setup.sources + [setup.cage, setup.target]
                offset_objects_edit = [o for o in objects if o not in do_not_offset_objects_edit]

                do_not_offset_objects_preview = [setup.projection_target, setup.cage]
                offset_objects_preview = [o for o in objects if o not in do_not_offset_objects_preview]

                offset = (0, CAGE_SCENE_OFFSET, CAGE_SCENE_OFFSET)

                setup.object_offset_edit = cls._offset_objects(offset_objects_edit, offset)
                setup.object_offset_preview = cls._offset_objects(offset_objects_preview, offset)

                node = bpy.data.node_groups.get("SN_ClipRayDistance")

                if node is None:
                    node = cls.get_prototype_node(asset_clipping, "SN_ClipRayDistance")

                cls._apply_cage_portal_parameters(setup, uv_map, offset)
                # TODO : Need to register the apply_cage_clipping in the AssetSetup, to trigger the clipping application
                # only when preview bake is turned on. Before the high poly model might not have material yet and I want
                # it to be inserted beetween the baker material and the material output node
                cls._apply_cage_clipping_parameters(setup, node, max_ray_distance)

                return setup

            except Exception:
                LOG.error("Preparation Failed")
                setup.cleanup()

                # The prototype itself was appended from the
                # external blend and must also be removed.
                cls._remove_object(prototype_portal)
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
        return offset

    @classmethod
    def _apply_cage_portal_parameters(
        cls,
        setup: AssetSetup,
        uv_map: str,
        offset: tuple[float, float, float],
    ):
        definition = registry_definition.get_custom("BAKE_PORTAL_PREVIEW")
        if definition is None:
            LOG.error("Parameter definition not found")
            return

        cage_info = cls._get_cage_info(setup, uv_map, cls._negate_tuple(offset))
        snapshot = ParameterService.snapshot_asset(definition, cage_info)

        LOG.debug("Applying Cage Portal parameters")

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
    def _apply_cage_clipping_parameters(
        cls,
        setup: AssetSetup,
        node: bpy.types.NodeGroup,
        max_ray_distance: float,
    ):
        definition = registry_definition.get_custom("BAKE_CLIPPING_PREVIEW")
        if definition is None:
            LOG.error("Parameter definition not found")
            return

        source_info = cls._get_source_info(max_ray_distance=max_ray_distance)
        snapshot = ParameterService.snapshot_asset(definition, source_info)

        LOG.debug("Applying Cage Clipping parameters")

        if setup.sources is None:
            LOG.error("Source Objects are not registered properly")
            return

        materials = []

        for source in setup.sources:
            source_materials = [m for m in source.data.materials if m is not None]

            materials = list(set(materials + source_materials))

        parameter_context = ParameterContext(
            object=setup.projection_target,
            scene=bpy.context.scene,
            materials=materials,
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
    ) -> CageInfo:
        cage_info = CageInfo(
            cage_object=setup.projection_cage,
            target_object=setup.target,
            offset=offset,
            uvmap=uv_map,
        )
        return cage_info

    @classmethod
    def _get_source_info(cls, max_ray_distance: float) -> SourcesInfo:
        sourc_info = SourcesInfo(
            max_ray_distance=max_ray_distance,
            shader="",
        )
        return sourc_info

    @classmethod
    def _negate_tuple(cls, t: tuple[float, float, float]) -> tuple[float, float, float]:
        return (t[0] * -1, t[1] * -1, t[2] * -1)
