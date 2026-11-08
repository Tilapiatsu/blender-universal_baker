from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

import bpy

from ..constant import LOG
from .material_injection import MaterialInjectionService
from .node_graph import NodeGraphService

LOG_SCOPE = "Material Override"


class MaterialTarget(StrEnum):
    DATA = "DATA"
    OBJECT = "OBJECT"


@dataclass
class MaterialSnapshot:
    object_name: str
    material_names: list[tuple[MaterialTarget, str | None]] = field(default_factory=list)
    temporary_material_names: list[str] = field(default_factory=list)

    @property
    def object(self) -> bpy.types.Object | None:
        if self.object_name not in bpy.data.objects:
            return None

        return bpy.data.objects[self.object_name]

    @property
    def materials(self) -> list[bpy.types.Material | None]:
        materials = []
        for target, mat in self.material_names:
            if mat is None:
                materials.append(None)
                continue

            if mat not in bpy.data.materials:
                materials.append(None)
                continue

            materials.append(bpy.data.materials[mat])

        return materials

    @property
    def target_materials(self) -> list[tuple[MaterialTarget, bpy.types.Material | None]]:
        target_materials = []
        for target, mat in self.material_names:
            if mat is None:
                target_materials.append((target, None))
                continue

            if mat not in bpy.data.materials:
                target_materials.append((target, None))
                continue

            target_materials.append((target, bpy.data.materials[mat]))

        return target_materials

    @property
    def temporary_materials(self) -> list[bpy.types.Material]:
        temporary_materials = []
        for m in self.temporary_material_names:
            mat = bpy.data.materials.get(m)
            if mat is None:
                continue

            temporary_materials.append(mat)

        return temporary_materials


class MaterialOverrideService:
    @staticmethod
    def apply(
        objects: list[bpy.types.Object],
        material: bpy.types.Material,
        target: MaterialTarget = MaterialTarget.OBJECT,
        inject: bool = False,
    ) -> list[MaterialSnapshot]:

        with LOG.scope(LOG_SCOPE):
            snapshots = []

            injected_materials: dict[bpy.types.Material, bpy.types.Material] = {}

            stored_instances = []
            for obj in objects:
                if obj.type != "MESH":
                    continue

                # NOTE: Check if the object has muliple users and prevent to register snapshot multiple times
                # if obj.data.name in stored_instances:
                #     continue

                if obj.data.users > 1:
                    stored_instances.append(obj.data.name)

                material_names = [
                    (MaterialTarget(slot.link), slot.material.name)
                    for slot in obj.material_slots
                    if slot.material is not None
                ]

                LOG.debug(f"Storing materials for {obj.name} : {material_names}")

                snapshot = MaterialSnapshot(
                    object_name=obj.name,
                    material_names=material_names,
                )

                # NOTE: add a Material slot if missing
                if len(obj.material_slots) == 0:
                    obj.data.materials.append(None)

                for index, slot in enumerate(obj.material_slots):
                    if inject:
                        # NOTE: Reuse already injected node
                        if slot.material in injected_materials:
                            LOG.debug(f"Reuse Injected Material : {injected_materials[slot.material].name}")
                            slot.link = target.value
                            slot.material = injected_materials[slot.material]
                            continue

                        # NOTE: No material assigned -> Override instead of inject
                        if slot.material is None:
                            LOG.debug("Empty Slot : Override material")
                            slot.link = target.value
                            slot.material = material
                            continue

                        output_node = NodeGraphService.find_material_output(slot.material.node_tree)

                        volume_node = NodeGraphService.get_input(output_node, "Volume")
                        displacement_node = NodeGraphService.get_input(output_node, "Displacement")

                        # NOTE: Bypass injection because no other material socket are used -> Override material instead
                        if (volume_node is None and displacement_node is None) or (
                            volume_node is not None
                            and not volume_node.is_linked
                            and displacement_node is not None
                            and not displacement_node.is_linked
                        ):
                            LOG.debug(f"No Injection Needed : Override Material {slot.material.name}")
                            slot.link = target.value
                            slot.material = material
                            continue

                        # NOTE: Doing injection
                        i_material = slot.material.copy()
                        injected_materials[slot.material] = i_material

                        snapshot.temporary_material_names.append(i_material.name)

                        LOG.debug(f"Inject Material : {i_material.name} into {slot.material.name}")

                        MaterialInjectionService.inject(material, i_material)
                        slot.link = target.value
                        slot.material = i_material

                    # NOTE: Override
                    else:
                        slot.link = target.value
                        slot.material = material

                    LOG.debug(f"Apply material {material.name} to slot {index}")

                snapshots.append(snapshot)

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

                # NOTE: Remove all materials if the object didn't had materials at the first place
                if not len(snapshot.material_names):
                    obj.data.materials.clear()

                for index, target_material in enumerate(snapshot.target_materials):
                    if obj.material_slots is None or index >= len(obj.material_slots):
                        continue

                    target, material = target_material

                    LOG.debug(f"Restoring material slot {index} : {material.name if material is not None else 'EMPTY'}")
                    if target_material is None:
                        LOG.error(f"Material {snapshot.material_names[index]} not found, can't recover")
                        continue

                    obj.material_slots[index].link = target.value
                    obj.material_slots[index].material = material

                for m in snapshot.temporary_materials:
                    bpy.data.materials.remove(m)
