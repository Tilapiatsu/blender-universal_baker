from __future__ import annotations

from dataclasses import dataclass

import bpy


@dataclass
class MaterialSnapshot:
    object: bpy.types.Object
    materials: list[bpy.types.Material | None]


class MaterialOverrideService:
    @staticmethod
    def apply(
        material: bpy.types.Material,
    ) -> list[MaterialSnapshot]:

        # ISSUE: When restoring, the previous materials didn't get reapplied to the objects properly
        snapshots = []

        for obj in bpy.context.scene.objects:
            if obj.type != "MESH":
                continue

            snapshots.append(
                MaterialSnapshot(
                    object=obj,
                    materials=[slot.material for slot in obj.material_slots],
                )
            )

            # NOTE: add a Material slot if missing
            if len(obj.material_slots) == 0:
                obj.data.materials.append(None)

            for slot in obj.material_slots:
                slot.material = material

        return snapshots

    @staticmethod
    def restore(
        snapshots: list[MaterialSnapshot],
    ):

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

                obj.material_slots[index].material = material
