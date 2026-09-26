from __future__ import annotations

import bpy


class ObjectRemoval:
    @classmethod
    def remove_object(cls, obj: bpy.data.Object):
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

        NodeRemoval.remove_nodes(node_groups + geo_nodes)


class MaterialRemoval:
    @classmethod
    def remove_material(cls, material: bpy.types.Material):
        material.use_nodes = True
        node_groups = [n.node_tree for n in material.node_tree.nodes if n.type == "GROUP"]

        bpy.data.materials.remove(
            material,
            do_unlink=True,
        )

        NodeRemoval.remove_nodes(node_groups)


class NodeRemoval:
    @classmethod
    def remove_nodes(cls, nodes: list[bpy.types.NodeTree], count: int | None = None):
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
            cls.remove_nodes(remaining, new_count)
