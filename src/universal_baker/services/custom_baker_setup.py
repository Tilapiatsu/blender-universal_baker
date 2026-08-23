from __future__ import annotations

import bpy

from ..runtime.baker_setup import BakerSetup
from .baker_asset import BakerAssetService
from ..resources.baker_asset import BakerAsset
from ..constant import LOG

LOG_SCOPE = "Custom Baker Setup Service"


class CustomBakerSetupError(RuntimeError):
    pass


class CustomBakerSetupService:
    def __init__(self):
        self.baker_asset_service = BakerAssetService()

    def prepare(self, asset: BakerAsset, target: bpy.types.Object) -> BakerSetup:
        with LOG.scope(LOG_SCOPE):
            LOG.debug(f"Prepare setup for {target.name}")
            prototype = self.baker_asset_service.load_prototype(asset)

            setup = BakerSetup()

            try:
                bake_object = self._duplicate_target(target)

                setup.target = bake_object
                setup.temporary_objects.append(bake_object)

                self._copy_material(prototype, bake_object, setup)
                self._copy_modifiers(prototype, bake_object)

                return setup

            except Exception:
                LOG.error("Preparation Failed")
                setup.cleanup()

                # The prototype itself was appended from the
                # external blend and must also be removed.
                self._remove_object(prototype)

                raise

    def _duplicate_target(self, target: bpy.types.Object) -> bpy.types.Object:
        LOG.debug("Duplicate Target")
        bake_object = target.copy()

        if target.data is not None:
            bake_object.data = target.data.copy()

        bake_object.name = f"UBK_TMP_{target.name}"

        # Link it to the same collection as the target.
        for collection in target.users_collection:
            collection.objects.link(bake_object)

        return bake_object

    def _copy_material(self, prototype: bpy.types.Object, target: bpy.types.Object, setup: BakerSetup) -> None:
        material = prototype.active_material

        if material is None:
            raise CustomBakerSetupError("Custom baker prototype does not have an active material.")

        material_copy = material.copy()

        material_copy.name = f"UBK_TMP_{material.name}"

        LOG.debug(f"Assign {material_copy.name} to {target.name}")
        target.data.materials.clear()
        target.data.materials.append(material_copy)

        setup.temporary_materials.append(material_copy)

    def _copy_modifiers(self, prototype: bpy.types.Object, target: bpy.types.Object) -> None:
        for source_modifier in prototype.modifiers:
            LOG.debug(f"Copying modifier {source_modifier.name} to {target.name}")
            modifier = target.modifiers.new(
                name=source_modifier.name,
                type=source_modifier.type,
            )

            self._copy_rna_properties(
                source_modifier,
                modifier,
            )

    def _copy_rna_properties(self, source, destination) -> None:
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

    def _remove_object(self, obj: bpy.types.Object | None) -> None:
        if obj is None:
            return

        try:
            bpy.data.objects.remove(
                obj,
                do_unlink=True,
            )
        except (ReferenceError, RuntimeError):
            pass
