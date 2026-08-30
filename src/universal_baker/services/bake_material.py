from __future__ import annotations

from dataclasses import dataclass, field

import bpy
from ..constant import LOG, BAKE_MATERIAL_NAME


LOG_SCOPE = "Bake Material"


class BakeMaterialError(RuntimeError):
    pass


@dataclass
class MaterialAssignment:
    """
    Snapshot of the material slots of one object.
    """

    object_name: str
    material_names: list[str | None] = field(default_factory=list)

    @property
    def object(self) -> bpy.types.Object | None:
        if self.object_name not in bpy.data.objects:
            return None

        return bpy.data.objects[self.object_name]

    @property
    def materials(self) -> list[bpy.types.Material | None]:
        materials = []
        for mat in self.material_names:
            if mat is None:
                materials.append(None)
                continue

            if mat not in bpy.data.materials:
                materials.append(None)
                continue

            materials.append(bpy.data.materials[mat])

        return materials


@dataclass
class BakeMaterialSetup:
    """
    Runtime state for temporary bake materials.

    The setup owns all materials it created and knows how to
    restore the original material assignments.
    """

    assignments: list[MaterialAssignment] = field(default_factory=list)
    temporary_materials: list[bpy.types.Material] = field(default_factory=list)
    _restored: bool = False

    def restore(self) -> None:
        LOG.debug("Restoring Initial Materials")
        if self._restored:
            return

        for assignment in self.assignments:
            obj = assignment.object

            if obj is None:
                LOG.error(f"{assignment.object_name} cannot be found. Resore skipped...")
                continue

            # The object may have been deleted by Blender/undo.
            try:
                materials = obj.data.materials
            except (ReferenceError, AttributeError):
                continue

            materials.clear()

            for material in assignment.materials:
                LOG.debug(f"Restoring Material: {material.name if material is not None else 'EMPTY'}")
                materials.append(material)

        self._restored = True

    def cleanup(self) -> None:
        """
        Restore original materials and remove temporary materials.
        """

        self.restore()

        LOG.debug("Cleanup Temporary Materials")
        for material in self.temporary_materials:
            if material is None:
                continue

            try:
                if material.users == 0:
                    LOG.debug(f"Removing Material: {material.name}")
                    bpy.data.materials.remove(material)
            except ReferenceError:
                pass

        self.temporary_materials.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()

        return False


class BakeMaterialService:
    @staticmethod
    def bake_material_name(obj: bpy.types.Object, slot: int, material_name: str | None = None) -> str:
        return (
            f"UBK_TMP_{obj.name}_{BAKE_MATERIAL_NAME if material_name is None else material_name}_{str(slot).zfill(2)}"
        )

    @staticmethod
    def replace_materials(
        obj: bpy.types.Object,
        materials: list[bpy.types.Material | None],
        setup: BakeMaterialSetup,
    ) -> None:

        current = obj.data.materials
        current.clear()

        for material in materials:
            if material is not None:
                material = material.copy()

                setup.temporary_materials.append(material)

            current.append(material)

    @classmethod
    def prepare(cls, objects: list[bpy.types.Object]) -> BakeMaterialSetup:
        with LOG.scope(LOG_SCOPE):
            LOG.debug("Preparing bake materials")
            setup = BakeMaterialSetup()

            try:
                for obj in objects:
                    cls._prepare_object(obj, setup)

                return setup

            except Exception:
                setup.cleanup()
                raise

    @classmethod
    def _prepare_object(
        cls,
        obj: bpy.types.Object,
        setup: BakeMaterialSetup,
    ) -> None:

        try:
            original_materials = [m.name for m in obj.data.materials if m is not None]
        except (ReferenceError, AttributeError) as exc:
            raise BakeMaterialError(f"Object '{obj.name}' does not have material slots.") from exc

        setup.assignments.append(
            MaterialAssignment(
                object_name=obj.name,
                material_names=original_materials,
            )
        )

        # NOTE: Add one virtual empty slot to make sure it get populated with one bake material right after
        if len(original_materials) == 0:
            original_materials.append(None)

        temporary_materials = []

        for slot, material_name in enumerate(original_materials):
            if material_name is None:
                material = cls._create_bake_material(obj, slot)
                material_name = material.name

            if material_name not in bpy.data.materials:
                LOG.error(f"Material {material_name} not found")
                continue

            material = bpy.data.materials[material_name]
            temporary = material.copy()
            temporary.name = cls.bake_material_name(obj, slot, material_name)
            temporary_materials.append(temporary)
            setup.temporary_materials.append(temporary)

        materials = obj.data.materials
        materials.clear()

        for material in temporary_materials:
            LOG.debug(f"Assign Temporary Material {material.name} to {obj.name}")
            materials.append(material)

    @classmethod
    def _create_bake_material(
        cls,
        obj: bpy.types.Object,
        slot: int,
        material_name: str | None = None,
    ) -> bpy.types.Material:
        name = cls.bake_material_name(obj, slot, material_name)

        if name in bpy.data.materials:
            LOG.debug(f"Reuse Existing Bake Material {name}")
            material = bpy.data.materials[name]
        else:
            LOG.debug(f"Create Bake Material {name}")
            material = bpy.data.materials.new(name=name)

        return material
