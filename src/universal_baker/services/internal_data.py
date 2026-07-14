import bpy

from ..constant import INTERNAL_DATA_NAME
from ..presets.output_preset import OutputPreset


class InternalDataService:
    TREE_NAME = INTERNAL_DATA_NAME

    @classmethod
    def get_tree(cls):
        tree = bpy.data.node_groups.get(cls.TREE_NAME)

        if tree is None:
            tree = bpy.data.node_groups.new(
                cls.TREE_NAME,
                "CompositorNodeTree",
            )

        return tree

    @classmethod
    def get_output_node(cls, name):
        tree = cls.get_tree()
        return tree.nodes.get(name)

    @classmethod
    def create_output_node(cls, name):
        tree = cls.get_tree()

        node = tree.nodes.new("CompositorNodeOutputFile")

        preset = OutputPreset(name, node)

        return preset

    @classmethod
    def ensure_output_node(cls, name):
        node = cls.get_output_node(name)

        if node is None:
            node = cls.create_output_node(name)

        return node

    @classmethod
    def remove_output_node(cls, name):
        tree = cls.get_tree()
        node = tree.nodes.get(name)

        if node is not None:
            tree.nodes.remove(node)
