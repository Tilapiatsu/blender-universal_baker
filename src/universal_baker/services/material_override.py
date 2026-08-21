from __future__ import annotations

from dataclasses import dataclass

import bpy

from ..constant import LOG

LOG_SCOPE = "Material Overide"


@dataclass
class MaterialSnapshot:
    object_name: str
    material_names: list[str | None]


class MaterialOverrideService:
    @staticmethod
    def apply(
        objects: list[bpy.types.Object],
        material: bpy.types.Material,
    ) -> list[MaterialSnapshot]:

        with LOG.scope(LOG_SCOPE):
            snapshots = []

            for obj in objects:
                if obj.type != "MESH":
                    continue

                LOG.debug(f"Storing materials for {obj.name}")
                snapshots.append(
                    MaterialSnapshot(
                        object_name=obj.name,
                        material_names=[slot.material.name for slot in obj.material_slots if slot.material is not None],
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
                obj = bpy.data.objects.get(snapshot.object_name)

                if obj is None:
                    LOG.error(f"Object {snapshot.object_name} not found, Can't recover")
                    continue
                # ISSUE: switch to preview / display then, move object then CTRL + Z finally disable preview / display
                # make snapshot invalid
                # ReferenceError on object stored in shapshots -> Should I store obj name instead ? What happen if the user rename an object
                # After CTRL + Z : The previous viewport state got lost
                # should this use the context manager ? with ... : for it to always restore in case of problems

                LOG.debug(f"Restoring materials for {obj.name}")

                # NOTE: Remove all materials the object didn't had materials at the first place
                if not len(snapshot.material_names):
                    obj.data.materials.clear()

                for index, material_name in enumerate(snapshot.material_names):
                    if obj.material_slots is None or index >= len(obj.material_slots):
                        continue

                    LOG.debug(
                        f"Restoring material slot {index} : {material_name if material_name is not None else 'EMPTY'}"
                    )
                    if material_name is None:
                        LOG.error(f"Material {material_name} not found, can't recover")
                        return

                    material = bpy.data.materials.get(material_name)
                    obj.material_slots[index].material = material
