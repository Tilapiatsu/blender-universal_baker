from __future__ import annotations

from typing import ClassVar

import bpy


class NodeCopyError(RuntimeError):
    """Raised when a node cannot be copied."""


class NodeCopyService:
    """Copy nodes and links between Blender node trees."""

    # Properties managed separately or not appropriate to copy.
    _SKIP_PROPERTIES: ClassVar = {
        "rna_type",
        "name",
        "type",
        "bl_idname",
        "inputs",
        "outputs",
        "internal_links",
        "dimensions",
        "location",
        "width",
        "height",
        "parent",
        "select",
        "select_node",
        "hide",
    }

    @classmethod
    def copy_node(
        cls,
        source_node: bpy.types.Node,
        target_tree: bpy.types.NodeTree,
    ) -> bpy.types.Node:
        """
        Create a copy of source_node in target_tree.

        This copies:
            - Writable RNA properties
            - Node custom properties
            - Socket default values
            - Node location and dimensions
            - Node label, color and display settings

        External datablocks remain shared references.
        """

        try:
            target_node = target_tree.nodes.new(
                source_node.bl_idname,
            )

        except Exception as exc:
            raise NodeCopyError(f"Could not create node '{source_node.bl_idname}'.") from exc

        try:
            cls._copy_rna_properties(
                source_node,
                target_node,
            )

            cls._copy_custom_properties(
                source_node,
                target_node,
            )

            cls._copy_socket_defaults(
                source_node,
                target_node,
            )

            cls._copy_display_properties(
                source_node,
                target_node,
            )

            return target_node

        except Exception:
            # Avoid leaving a partially copied node behind.
            target_tree.nodes.remove(target_node)

            raise

    @classmethod
    def _copy_rna_properties(
        cls,
        source_node: bpy.types.Node,
        target_node: bpy.types.Node,
    ) -> None:
        """
        Copy writable RNA properties.

        Properties that cannot be assigned directly are skipped.
        """
        if source_node.type == "MENU_SWITCH":
            for j, item in enumerate(source_node.enum_items):
                if j >= len(target_node.enum_items):
                    target_node.enum_items.new(item.name)
                else:
                    target_node.enum_items[j].name = item.name

        for prop in source_node.bl_rna.properties:
            identifier = prop.identifier

            if identifier in cls._SKIP_PROPERTIES:
                continue

            if prop.is_readonly:
                continue

            try:
                value = getattr(
                    source_node,
                    identifier,
                )

                # Do not attempt to copy RNA collections.
                if prop.type == "COLLECTION":
                    continue

                # Pointer properties can represent datablocks,
                # node trees, objects, images, etc.
                #
                # Preserve the reference instead of duplicating it.
                setattr(
                    target_node,
                    identifier,
                    value,
                )

            except (
                AttributeError,
                TypeError,
                ValueError,
                RuntimeError,
            ):
                # Some node properties depend on node configuration.
                # Those properties may require specialized handling.
                continue

    @classmethod
    def _copy_custom_properties(
        cls,
        source_node: bpy.types.Node,
        target_node: bpy.types.Node,
    ) -> None:
        """Copy Blender ID properties attached to the node."""

        try:
            for key in source_node:
                if key == "_RNA_UI":
                    continue

                try:
                    target_node[key] = source_node[key]

                except (
                    TypeError,
                    ValueError,
                    RuntimeError,
                ):
                    continue

        except (AttributeError, TypeError):
            pass

    @classmethod
    def _copy_socket_defaults(
        cls,
        source_node: bpy.types.Node,
        target_node: bpy.types.Node,
    ) -> None:
        """
        Copy default values of matching input and output sockets.

        Socket matching prefers identifiers and falls back to
        socket names and indices.
        """

        cls._copy_socket_collection(
            source_node.inputs,
            target_node.inputs,
        )

        cls._copy_socket_collection(
            source_node.outputs,
            target_node.outputs,
        )

    @classmethod
    def _copy_socket_collection(
        cls,
        source_sockets,
        target_sockets,
    ) -> None:

        for index, source_socket in enumerate(source_sockets):
            target_socket = cls._find_matching_socket(
                source_socket,
                target_sockets,
                index,
            )

            if target_socket is None:
                continue

            if not hasattr(source_socket, "default_value"):
                continue

            if not hasattr(target_socket, "default_value"):
                continue

            try:
                target_socket.default_value = source_socket.default_value

            except (
                AttributeError,
                TypeError,
                ValueError,
                RuntimeError,
            ):
                continue

    @staticmethod
    def _find_matching_socket(
        source_socket,
        target_sockets,
        index: int,
    ):
        """Find the equivalent socket on a copied node."""

        identifier = getattr(
            source_socket,
            "identifier",
            None,
        )

        if identifier:
            for target_socket in target_sockets:
                if target_socket.identifier == identifier:
                    return target_socket

        # Fallback to name.
        for target_socket in target_sockets:
            if target_socket.name == source_socket.name:
                return target_socket

        # Final fallback to the original socket index.
        if index < len(target_sockets):
            return target_sockets[index]

        return None

    @classmethod
    def _copy_display_properties(
        cls,
        source_node: bpy.types.Node,
        target_node: bpy.types.Node,
    ) -> None:
        """Copy node editor presentation properties."""

        target_node.name = source_node.name
        target_node.label = source_node.label

        target_node.location = source_node.location
        target_node.width = source_node.width
        target_node.height = source_node.height

        target_node.hide = source_node.hide
        target_node.mute = source_node.mute

        try:
            target_node.color = source_node.color
            target_node.use_custom_color = source_node.use_custom_color

        except (AttributeError, TypeError):
            pass

        try:
            target_node.show_options = source_node.show_options
            target_node.show_preview = source_node.show_preview

        except (AttributeError, TypeError):
            pass

    @classmethod
    def copy_nodes(
        cls,
        source_tree,
        target_tree,
        source_nodes,
    ):
        node_mapping = {}

        try:
            for source_node in source_nodes:
                copied_node = cls.copy_node(
                    source_node,
                    target_tree,
                )

                node_mapping[source_node] = copied_node

            for source_node, copied_node in node_mapping.items():
                source_parent = source_node.parent

                if source_parent is None:
                    continue

                copied_parent = node_mapping.get(
                    source_parent,
                )

                if copied_parent is not None:
                    copied_node.parent = copied_parent

            cls.copy_links(
                source_tree,
                target_tree,
                node_mapping,
            )

            return node_mapping

        except Exception:
            for copied_node in reversed(list(node_mapping.values())):
                try:
                    target_tree.nodes.remove(copied_node)

                except (ReferenceError, RuntimeError):
                    pass

            raise NodeCopyError

    @classmethod
    def copy_links(
        cls,
        source_tree: bpy.types.NodeTree,
        target_tree: bpy.types.NodeTree,
        node_mapping: dict,
    ) -> None:
        """
        Copy links whose source and destination nodes
        both exist in node_mapping.
        """

        for source_link in source_tree.links:
            source_from_node = source_link.from_node
            source_to_node = source_link.to_node

            # Do not copy links outside the selected graph.
            if source_from_node not in node_mapping:
                continue

            if source_to_node not in node_mapping:
                continue

            target_from_node = node_mapping[source_from_node]

            target_to_node = node_mapping[source_to_node]

            from_index = list(source_from_node.outputs).index(source_link.from_socket)

            to_index = list(source_to_node.inputs).index(source_link.to_socket)

            from_socket = cls._find_matching_socket(
                source_link.from_socket,
                target_from_node.outputs,
                from_index,
            )

            to_socket = cls._find_matching_socket(
                source_link.to_socket,
                target_to_node.inputs,
                to_index,
            )

            if from_socket is None or to_socket is None:
                raise NodeCopyError(
                    "Could not find matching sockets "
                    f"for link between "
                    f"'{source_from_node.name}' and "
                    f"'{source_to_node.name}'."
                )

            target_tree.links.new(
                from_socket,
                to_socket,
            )
