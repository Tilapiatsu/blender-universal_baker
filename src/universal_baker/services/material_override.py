from __future__ import annotations

from dataclasses import dataclass

import bpy

from ..constant import LOG

LOG_SCOPE = "Material Overide"


@dataclass
class MaterialSnapshot:
    object: bpy.types.Object
    materials: list[bpy.types.Material | None]


class MaterialOverrideService:
    @staticmethod
    def apply(
        material: bpy.types.Material,
    ) -> list[MaterialSnapshot]:

        with LOG.scope(LOG_SCOPE):
            snapshots = []

            for obj in bpy.context.scene.objects:
                if obj.type != "MESH":
                    continue

                LOG.debug(f"Storing materials for {obj.name}")
                snapshots.append(
                    MaterialSnapshot(
                        object=obj,
                        materials=[slot.material for slot in obj.material_slots],
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
                    continue

                # NOTE: Remove all materials the object didn't had materials at the first place
                if not len(snapshot.materials):
                    obj.data.materials.clear()

                for index, material in enumerate(snapshot.materials):
                    if index >= len(obj.material_slots):
                        continue

                    LOG.debug(f"Restoring material slot {index} : {material.name if material is not None else 'EMPTY'}")
                    obj.material_slots[index].material = material
