from __future__ import annotations

from contextlib import contextmanager

import bpy

from ..constant import LOG
from ..resources.asset_external import AssetExtrenal
from ..runtime.asset_setup import AssetSetup
from ..runtime.bake_objects import BakeObjects
from ..services.bake_material import BakeMaterialService
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

        # NOTE: Important to hide from rendering the base object. because it could pollute the baking for some
        # bakers ( AO, Diffuse ...)
        obj.hide_render = True

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
    def _duplicate_object(obj: bpy.types.Object) -> bpy.types.Object:
        LOG.debug(f"Duplicate object {obj.name}")
        bake_object = obj.copy()

        if obj.data is not None:
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
                duplicated_sources = []
                for o in bake_objects.source_objects:
                    duplicated_source = cls._prepare_object(o, prototype, setup)
                    duplicated_sources.append(duplicated_source)

                setup.sources = duplicated_sources
                setup.target = bake_objects.target_object
                # material_setup = BakeMaterialService.prepare(
                #     targets=[bake_objects.target_object], sources=duplicated_sources
                # )
                # setup.material_setup = material_setup
                setup.cage = bake_objects.cage_object

                return setup

            except Exception:
                LOG.error("Preparation Failed")
                setup.cleanup()

                # The prototype itself was appended from the
                # external blend and must also be removed.
                cls._remove_object(prototype)
                raise RuntimeError
