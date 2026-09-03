from __future__ import annotations

from dataclasses import dataclass, field

import bpy

from ..constant import LOG

LOG_SCOPE = "Material Override"


@dataclass
class MaterialSnapshot:
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


class MaterialOverrideService:
    @staticmethod
    def apply(
        objects: list[bpy.types.Object],
        material: bpy.types.Material,
    ) -> list[MaterialSnapshot]:

        with LOG.scope(LOG_SCOPE):
            snapshots = []

            stored_instances = []
            for obj in objects:
                if obj.type != "MESH":
                    continue

                # NOTE: Check if the object has muliple users and prevent to register snapshot multiple times
                if obj.data.name in stored_instances:
                    continue

                if obj.data.users > 1:
                    stored_instances.append(obj.data.name)

                material_names = [slot.material.name for slot in obj.material_slots if slot.material is not None]

                LOG.debug(f"Storing materials for {obj.name} : {material_names}")

                snapshots.append(
                    MaterialSnapshot(
                        object_name=obj.name,
                        material_names=material_names,
                    )
                )

                # NOTE: add a Material slot if missing
                if len(obj.material_slots) == 0:
                    obj.data.materials.append(None)

                for index, slot in enumerate(obj.material_slots):
                    LOG.debug(f"Apply material {material.name} to slot {index}")
                    slot.material = material

            return snapshots

    @staticmethod
    def restore(
        snapshots: list[MaterialSnapshot],
    ):

        with LOG.scope(LOG_SCOPE):
            for snapshot in snapshots:
                obj = snapshot.object

                if obj is None:
                    LOG.error(f"Object {snapshot.object_name} not found, Can't recover")
                    continue

                LOG.debug(f"Restoring materials for {obj.name}")

                # NOTE: Remove all materials the object didn't had materials at the first place
                if not len(snapshot.material_names):
                    obj.data.materials.clear()

                for index, material in enumerate(snapshot.materials):
                    if obj.material_slots is None or index >= len(obj.material_slots):
                        continue

                    LOG.debug(f"Restoring material slot {index} : {material.name if material is not None else 'EMPTY'}")
                    if material is None:
                        LOG.error(f"Material {snapshot.material_names[index]} not found, can't recover")
                        continue

                    obj.material_slots[index].material = material
