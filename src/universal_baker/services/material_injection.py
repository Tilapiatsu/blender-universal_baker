from __future__ import annotations

import bpy

from ..constant import LOG
from .node_copy import (
    NodeCopyService,
)
from .node_graph import (
    NodeGraphError,
    NodeGraphService,
)


class MaterialInjectionError(RuntimeError):
    """Raised when material injection fails."""


class MaterialInjectionService:
    """
    Inject a shader graph into an existing material.

    The default operation replaces only the target material's
    Surface connection.

    Volume, Displacement and other output connections remain
    untouched.
    """

    @classmethod
    def inject(
        cls,
        source_material: bpy.types.Material,
        target_material: bpy.types.Material,
        output_target: str = "ALL",
        input_name: str = "Surface",
    ) -> dict:
        """
        Copy the graph contributing to source Surface and
        inject it into target Surface.

        Parameters
        ----------
        source_material:
            Material providing the shader graph.

        target_material:
            Material receiving the copied graph.

        output_target:
            Material output target:
                ALL
                CYCLES
                EEVEE

        Returns
        -------
        dict
            Source-node to copied-node mapping.
        """

        if source_material is None:
            raise MaterialInjectionError("Source material is None.")

        if target_material is None:
            raise MaterialInjectionError("Target material is None.")

        if not source_material.use_nodes:
            raise MaterialInjectionError(f"Source material '{source_material.name}' does not use nodes.")

        if source_material.node_tree is None:
            raise MaterialInjectionError("Source material has no node tree.")

        target_material.use_nodes = True

        source_tree = source_material.node_tree
        target_tree = target_material.node_tree

        if target_tree is None:
            raise MaterialInjectionError("Target material has no node tree.")

        # --------------------------------------------------
        # 1. Find source output and upstream graph
        # --------------------------------------------------

        LOG.debug(f"Injecting Material's {input_name} : {source_material.name} -> {target_material.name}")
        try:
            (
                source_output,
                source_surface,
                source_nodes,
            ) = NodeGraphService.collect_graph(
                source_material,
                target=output_target,
                input_name=input_name,
            )

        except NodeGraphError as exc:
            raise MaterialInjectionError(f"Could not collect the source {input_name} graph.") from exc

        # If the Surface socket is unconnected, there is no
        # shader graph to inject.
        if not source_surface.is_linked:
            raise MaterialInjectionError("Source Surface is not connected.")

        # Preserve the original source connection.
        source_surface_link = source_surface.links[0]

        source_shader_node = source_surface_link.from_node

        source_shader_socket = source_surface_link.from_socket

        # --------------------------------------------------
        # 2. Find target output
        # --------------------------------------------------

        try:
            target_output = NodeGraphService.find_material_output(
                target_tree,
                target=output_target,
            )

        except NodeGraphError as exc:
            raise MaterialInjectionError("Could not find target Material Output.") from exc

        target_surface = NodeGraphService.get_input(
            target_output,
        )

        # --------------------------------------------------
        # 3. Copy graph
        # --------------------------------------------------

        copied_nodes = []

        try:
            node_mapping = NodeCopyService.copy_nodes(
                source_tree,
                target_tree,
                source_nodes,
            )

            copied_nodes.extend(node_mapping.values())

            # --------------------------------------------------
            # 4. Find copied shader output
            # --------------------------------------------------

            copied_shader_node = node_mapping[source_shader_node]

            copied_shader_socket = NodeCopyService._find_matching_socket(
                source_shader_socket,
                copied_shader_node.outputs,
                list(source_shader_node.outputs).index(source_shader_socket),
            )

            if copied_shader_socket is None:
                raise MaterialInjectionError("Could not find copied shader output socket.")

            # --------------------------------------------------
            # 5. Replace target Surface connection
            # --------------------------------------------------

            # Remove only links connected to Surface.
            #
            # Volume, Displacement and Thickness are untouched.

            existing_surface_links = list(target_surface.links)

            for link in existing_surface_links:
                target_tree.links.remove(link)

            target_tree.links.new(
                copied_shader_socket,
                target_surface,
            )

            return node_mapping

        except Exception as exc:
            # --------------------------------------------------
            # 6. Rollback copied nodes
            # --------------------------------------------------

            # The graph copy failed. Remove the newly created
            # nodes so the target isn't left partially modified.

            for node in reversed(copied_nodes):
                try:
                    target_tree.nodes.remove(node)

                except (ReferenceError, RuntimeError):
                    pass

            if isinstance(
                exc,
                MaterialInjectionError,
            ):
                raise

            raise MaterialInjectionError("Material Surface injection failed.") from exc

    @classmethod
    def copy(
        cls,
        source_material: bpy.types.Material,
        target_material: bpy.types.Material,
    ):
        target_material.use_nodes = True
        dst_tree = target_material.node_tree
        dst_tree.nodes.clear()
        src_tree = source_material.node_tree
        node_mapping = {}

        for node in src_tree.nodes:
            new_node = dst_tree.nodes.new(type=node.bl_idname)
            new_node.location = node.location
            new_node.width = node.width
            new_node.name = node.name

            if node.type in ["MENU_SWITCH", "MAP_RANGE"]:
                new_node.data_type = node.data_type

            for i, input_sock in enumerate(node.inputs):
                if i < len(new_node.inputs) and not input_sock.is_linked:
                    try:
                        new_input = new_node.inputs[i]
                        if node.type == "MENU_SWITCH":
                            for j, item in enumerate(node.enum_items):
                                if j >= len(new_node.enum_items):
                                    new_node.enum_items.new(item.name)
                                else:
                                    new_node.enum_items[j].name = item.name

                        if hasattr(new_input, "default_value"):
                            new_input.default_value = input_sock.default_value

                    except AttributeError as e:
                        LOG.error(str(e))

            if hasattr(node, "image") and hasattr(new_node, "image"):
                new_node.image = node.image

            if hasattr(node, "node_tree"):
                new_node.node_tree = node.node_tree

            if hasattr(node, "operation"):
                new_node.operation = node.operation

            if hasattr(node, "attribute_name"):
                new_node.attribute_name = node.attribute_name

            if hasattr(node, "attribute_type"):
                new_node.attribute_type = node.attribute_type

            if hasattr(node, "inside"):
                new_node.inside = node.inside

            node_mapping[node] = new_node

        for link in src_tree.links:
            from_node = node_mapping.get(link.from_node)
            to_node = node_mapping.get(link.to_node)

            if from_node and to_node:
                from_sock_idx = list(link.from_node.outputs).index(link.from_socket)
                to_sock_idx = list(link.to_node.inputs).index(link.to_socket)

                if not len(from_node.outputs) or not len(to_node.inputs):
                    continue

                dst_tree.links.new(from_node.outputs[from_sock_idx], to_node.inputs[to_sock_idx])
