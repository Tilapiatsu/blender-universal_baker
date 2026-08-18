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

            for index, material in enumerate(snapshot.materials):
                if index >= len(obj.material_slots):
                    continue

                obj.material_slots[index].material = material
