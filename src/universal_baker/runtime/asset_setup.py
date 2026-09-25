from __future__ import annotations

from dataclasses import dataclass, field

import bpy

from ..constant import LOG
from ..services.bake_material import BakeMaterialSetup
from ..services.object_offset import ObjectOffset

LOG_SCOPE = "Asset Setup"


@dataclass
class AssetSetup:
    """
    Temporary Blender state created for one custom baker operation.
    """

    target: bpy.types.Object | None = None
    cage: bpy.types.Object | None = None
    projection_cage: bpy.types.Object | None = None
    projection_target: bpy.types.Object | None = None
    sources: list[bpy.types.Object] | None = None
    temporary_objects: list[bpy.types.Object] = field(default_factory=list)
    temporary_materials: list[bpy.types.Material] = field(default_factory=list)
    temporary_node_group: list[bpy.types.NodeTree] = field(default_factory=list)
    temporary_modifiers: list[tuple[bpy.types.Object, str]] = field(default_factory=list)
    material_setup: BakeMaterialSetup | None = None
    object_offset_edit: ObjectOffset | None = None
    object_offset_preview: ObjectOffset | None = None

    def cleanup(self) -> None:
        """
        Remove all temporary Blender datablocks created by this setup.
        """
        with LOG.scope(LOG_SCOPE):
            LOG.debug("Cleaning up AssetSetup")

            if self.material_setup is not None:
                self.material_setup.cleanup()
                self.material_setup = None

            # Objects first.
            for obj in list(self.temporary_objects):
                if obj is None:
                    continue

                if obj.name in bpy.data.objects:
                    LOG.debug(f"Remove Temporary Object: {obj.name}")
                    data = obj.data
                    geo_nodes = [m.node_group for m in obj.modifiers if m.type == "NODES"]

                    node_groups = []
                    for n in geo_nodes:
                        for node in n.nodes:
                            if node.type == "GROUP":
                                node_groups.append(node.node_tree)

                    bpy.data.objects.remove(
                        obj,
                        do_unlink=True,
                    )
                    if data.users == 0:
                        bpy.data.meshes.remove(data)

                    self._remove_nodes(node_groups + geo_nodes)

            self.temporary_objects.clear()

            # Materials created specifically by the setup.
            for material in list(self.temporary_materials):
                if material is None:
                    continue

                if material.name in bpy.data.materials:
                    LOG.debug(f"Remove Temporary Material: {material.name}")
                    material.use_nodes = True
                    node_groups = [n.node_tree for n in material.node_tree.nodes if n.type == "GROUP"]

                    bpy.data.materials.remove(
                        material,
                        do_unlink=True,
                    )

                    self._remove_nodes(node_groups)

                    for node in node_groups:
                        if node.users == 0:
                            bpy.data.node_groups.remove(node)

            self.temporary_materials.clear()

            self.temporary_modifiers.clear()

            if self.object_offset_edit is not None:
                self.object_offset_edit.revert()
                self.object_offset_edit = None

            if self.object_offset_preview is not None:
                self.object_offset_preview.revert()
                self.object_offset_preview = None

    def _remove_nodes(self, nodes: list[bpy.types.NodeTree], count: int | None = None):
        if count is None:
            count = len(nodes)

        if count == 0:
            return

        new_count = count
        remaining = []
        for node in nodes:
            if node.users == 0:
                bpy.data.node_groups.remove(node)
                new_count -= 1
            else:
                remaining.append(node)

        if new_count == 0 or new_count == count:
            return
        else:
            self._remove_nodes(remaining, new_count)

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.cleanup()

        return False


@dataclass
class BakerExecution:
    target: bpy.types.Object
    cage: bpy.types.Object
    sources: list[bpy.types.Object] | None = None
    setup: AssetSetup | None = None

    def cleanup(self):
        if self.setup is not None:
            self.setup.cleanup()
