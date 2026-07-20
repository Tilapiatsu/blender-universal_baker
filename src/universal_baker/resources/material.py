from __future__ import annotations

from dataclasses import dataclass, field

import bpy


@dataclass(slots=True)
class MaterialResource:
    """
    Runtime wrapper around a material used during baking.

    It stores both the material datablock and every temporary
    modification applied during the bake so it can be restored
    afterwards.
    """

    material: bpy.types.Material | None = None
    node_tree: bpy.types.NodeTree | None = None

    image_node: bpy.types.ShaderNodeTexImage | None = None
    created_image_node: bool = False
    previous_active_node: bpy.types.Node | None = None
    uv_map_name: str = ""

    output_socket: bpy.types.NodeSocket | None = None
    temporary_nodes: list[bpy.types.Node] = field(default_factory=list)
    temporary_links: list[tuple] = field(default_factory=list)

    object: bpy.types.Object | None = None
    material_index: int = 0
    created_material: bool = False

    prepared: bool = False
    restored: bool = False
    temporary: bool = False

    @property
    def exists(self) -> bool:
        return self.material is not None

    @property
    def uses_nodes(self) -> bool:
        if self.material is None:
            return False

        return self.material.use_nodes

    def ensure_nodes(self) -> None:
        """
        Enable node-based shading if necessary.
        """
        if self.material is None:
            return

        if not self.material.use_nodes:
            self.material.use_nodes = True

        self.node_tree = self.material.node_tree

    def activate_image_node(self) -> None:
        """
        Make the bake image node the active node.
        """

        if self.node_tree is None:
            return

        if self.image_node is None:
            return

        self.previous_active_node = self.node_tree.nodes.active
        self.node_tree.nodes.active = self.image_node

    def restore_active_node(self) -> None:
        """
        Restore the original active node.
        """

        if self.node_tree is None:
            return

        self.node_tree.nodes.active = self.previous_active_node

    def mark_prepared(self) -> None:
        self.prepared = True

    def mark_restored(self) -> None:
        self.restored = True
