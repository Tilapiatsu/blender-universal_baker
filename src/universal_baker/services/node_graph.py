from __future__ import annotations

import bpy


class NodeGraphError(RuntimeError):
    """Raised when a node graph operation cannot be completed."""


class NodeGraphService:
    """Utilities for inspecting and traversing Blender node graphs."""

    @staticmethod
    def find_material_output(
        node_tree: bpy.types.NodeTree,
        target: str = "ALL",
    ) -> bpy.types.Node:
        """
        Find the active material output node.

        Parameters
        ----------
        node_tree:
            The material node tree.

        target:
            Blender output target:
                ALL
                CYCLES
                EEVEE

        Returns
        -------
        bpy.types.Node
            The matching active output node.
        """

        outputs = [node for node in node_tree.nodes if node.type == "OUTPUT_MATERIAL"]

        if not outputs:
            raise NodeGraphError("No Material Output node found.")

        # Prefer an active output matching the requested target.
        matching = [node for node in outputs if node.is_active_output and getattr(node, "target", "ALL") == target]

        if matching:
            return matching[0]

        # Blender generally has a single active output.
        active = [node for node in outputs if node.is_active_output]

        if active:
            return active[0]

        # Fallback for unusual or manually constructed node trees.
        return outputs[0]

    @staticmethod
    def get_input(
        output_node: bpy.types.Node,
        input_name: str = "Surface",
    ) -> bpy.types.NodeSocket:
        """Return the Surface input socket."""

        input_node = output_node.inputs.get(input_name)

        if input_node is None:
            raise NodeGraphError("Material Output has no Surface input.")

        return input_node

    @staticmethod
    def collect_upstream_nodes(
        output_socket: bpy.types.NodeSocket,
        include_frames: bool = True,
    ) -> set[bpy.types.Node]:
        """
        Collect all nodes contributing to output_socket.

        The output node itself is not included.

        This traverses all linked inputs of upstream nodes.
        """

        collected = set()
        pending = []

        # Start with nodes connected to the requested output socket.
        for link in output_socket.links:
            pending.append(link.from_node)

        while pending:
            node = pending.pop()

            if node in collected:
                continue

            collected.add(node)

            # Traverse all linked inputs.
            for input_socket in node.inputs:
                for link in input_socket.links:
                    upstream_node = link.from_node

                    if upstream_node not in collected:
                        pending.append(upstream_node)

        if include_frames:
            # A node may belong to a frame which is not otherwise
            # connected to the shader graph.
            #
            # Include parent frames so the copied hierarchy can
            # be reconstructed.
            frames = set()

            for node in tuple(collected):
                parent = node.parent

                while parent is not None:
                    if parent in frames:
                        break

                    frames.add(parent)
                    parent = parent.parent

            collected.update(frames)

        return collected

    @classmethod
    def collect_graph(
        cls,
        material: bpy.types.Material,
        target: str = "ALL",
        input_name: str = "Surface",
    ) -> tuple[
        bpy.types.Node,
        bpy.types.NodeSocket,
        set[bpy.types.Node],
    ]:
        """
        Collect the graph contributing to a material's Surface.

        Returns
        -------
        output_node, surface_socket, upstream_nodes
        """

        if not material.use_nodes or material.node_tree is None:
            raise NodeGraphError(f"Material '{material.name}' does not use nodes.")

        output_node = cls.find_material_output(
            material.node_tree,
            target=target,
        )

        surface_socket = cls.get_input(
            output_node,
            input_name,
        )

        upstream_nodes = cls.collect_upstream_nodes(
            surface_socket,
        )

        return (
            output_node,
            surface_socket,
            upstream_nodes,
        )
