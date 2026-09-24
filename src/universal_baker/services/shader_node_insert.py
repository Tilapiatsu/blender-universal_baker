from __future__ import annotations

from dataclasses import dataclass

import bpy

from ..constant import LOG


@dataclass(slots=True, frozen=True)
class InsertionSocketPair:
    from_node_name: str
    to_node_name: str
    input_socket: str
    output_socket: str


@dataclass(slots=True, frozen=True)
class InsertionState:
    material_name: str
    from_sockets: list[InsertionSocketPair]
    to_sockets: list[InsertionSocketPair]
    original_sockets: list[InsertionSocketPair]


class ShaderNodeInsert:
    def __init__(
        self,
        material: bpy.types.Material,
        node: bpy.types.Node,
        from_sockets: list[InsertionSocketPair],
        to_sockets: list[InsertionSocketPair],
    ):
        material.use_nodes = True

        self.material_name = material.name
        self.node_name = node.name

        self.insertion_state = InsertionState(
            material_name=material.name,
            from_sockets=from_sockets,
            to_sockets=to_sockets,
            original_sockets=self._get_original_sockets(material, from_sockets, to_sockets),
        )
        self._has_inserted = False

    @property
    def material(self) -> bpy.types.Material | None:
        return bpy.data.materials.get(self.material_name)

    @property
    def node(self) -> bpy.types.Node | None:
        return bpy.data.materials.get(self.node_name)

    def _connect_socket(self, node_tree, socket) -> bool:
        from_node = node_tree.nodes.get(socket.from_node_name)
        if from_node is None:
            return False
        to_node = node_tree.nodes.get(socket.to_node_name)
        if to_node is None:
            return False

        node_tree.links.new(from_node.outputs[socket.output_socket], to_node.inputs[socket.input_socket])

        return True

    def _get_original_sockets(
        self,
        material: bpy.types.Material,
        from_sockets: list[InsertionSocketPair],
        to_sockets: list[InsertionSocketPair],
    ) -> list[InsertionSocketPair]:
        node_tree = material.node_tree

        nodes_from = [n.from_node_name for n in from_sockets]
        nodes_to = [n.to_node_name for n in to_sockets]

        original_sockets: list[InsertionSocketPair] = []

        for n in node_tree.nodes:
            if n.name in nodes_from:
                for out in n.outputs:
                    if out.links[1] is None:
                        continue
                    o = out.link[1].to_node
                    if o is None:
                        continue

                    if o.name in nodes_to:
                        original_sockets.append(
                            InsertionSocketPair(
                                from_node_name=n.name,
                                to_node_name=o.name,
                                input_socket=out.link[1].to_socket.name,
                                output_socket=out.link[0].from_socket.name,
                            )
                        )

        return original_sockets

    def set_insert(self) -> bpy.types.Object:
        if self.material is None or self.node is None or self._has_inserted:
            return

        node_tree = self.material.node_tree
        node_mapping = {}

        new_node = node_tree.nodes.new(type=self.node.bl_idname)
        for i, input_sock in enumerate(self.node.inputs):
            if i < len(new_node.inputs) and not input_sock.is_linked:
                try:
                    new_node.inputs[i].default_value = input_sock.default_value
                except AttributeError:
                    pass

        if hasattr(self.node, "image") and hasattr(new_node, "image"):
            new_node.image = self.node.image

        if hasattr(self.node, "node_tree"):
            new_node.node_tree = self.node.node_tree

        node_mapping[self.node] = new_node

        for socket in self.insertion_state.from_sockets:
            if not self._connect_socket(node_tree, socket):
                return False

        for socket in self.insertion_state.to_sockets:
            if not self._connect_socket(node_tree, socket):
                return False

        self._has_inserted = True

        return self.material

    def revert_insert(self) -> None:
        if self.material is None or not self._has_inserted:
            return

        node_tree = self.material.node_tree

        node = node_tree.nodes.get(self.node_name)

        if node is not None:
            node.remove()

        for sock in self.insertion_state.original_sockets:
            from_node = node_tree.get(sock.from_node_name)
            if from_node is None:
                continue

            to_node = node_tree.get(sock.to_node_name)
            if to_node is None:
                continue

            node_tree.links.new(from_node.outputs[sock.output_socket], to_node.inputs[sock.input_socket])

        self._has_inserted = False

    def __enter__(self):
        return self.set_insert()

    def __exit__(self, exc_type, exc_value, traceback):
        self.revert_insert()
