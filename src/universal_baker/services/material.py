from __future__ import annotations

import bpy

from ..runtime.context import BakeContext
from ..resources.material import MaterialResource
from ..constant import BAKE_IMAGE_NODE_LABEL, BAKE_IMAGE_NODE_NAME, BAKE_MATERIAL_NAME


class MaterialService:
    """Manage temporary material modifications during baking."""

    @classmethod
    def prepare_target(cls, ctx: BakeContext) -> None:
        """
        Prepare the target object's active material for baking.
        """
        resource = ctx.material

        cls.acquire(resource, ctx)
        cls.ensure_nodes(resource)
        cls.ensure_image_node(resource)
        cls.assign_image(resource, ctx)
        cls.activate_image_node(resource)

        resource.mark_prepared()

    @classmethod
    def restore_target(cls, ctx: BakeContext) -> None:
        """
        Restore the material to its original state.
        """

        resource = ctx.material

        if not resource.prepared:
            return

        cls.restore_active_node(resource)
        cls.remove_temporary_nodes(resource)

        resource.mark_restored()

    @classmethod
    def acquire(cls, resource: MaterialResource, ctx: BakeContext) -> None:
        """
        Acquire the material used for baking.
        """

        obj = ctx.target

        if not obj.material_slots:
            cls._create_bake_material(obj, None)
            # raise RuntimeError(f"'{obj.name}' has no material.")

        slot = obj.material_slots[0]

        material = slot.material

        if material is None:
            cls._create_bake_material(obj, 0)
            # raise RuntimeError(f"Material slot is empty.")

        resource.object = obj
        resource.material_index = 0
        resource.material = material
        resource.node_tree = material.node_tree

    @classmethod
    def ensure_nodes(cls, resource: MaterialResource) -> None:
        """
        Ensure node-based shading is enabled.
        """
        material = resource.material

        if material is None:
            return

        if not material.use_nodes:
            material.use_nodes = True

        resource.node_tree = material.node_tree

    @classmethod
    def ensure_image_node(cls, resource: MaterialResource) -> None:
        """
        Find or create the bake image node.
        """

        tree = resource.node_tree

        if tree is None:
            return

        for node in tree.nodes:
            if node.type != "TEX_IMAGE":
                continue

            if node.label == BAKE_IMAGE_NODE_LABEL:
                resource.image_node = node
                return

        node = tree.nodes.new("ShaderNodeTexImage")

        node.label = BAKE_IMAGE_NODE_LABEL
        node.name = BAKE_IMAGE_NODE_NAME
        node.location = (-600, 300)
        resource.image_node = node
        resource.created_image_node = True

    @classmethod
    def assign_image(cls, resource: MaterialResource, ctx: BakeContext) -> None:
        if resource.image_node is None:
            return

        resource.image_node.image = ctx.image

    @classmethod
    def activate_image_node(cls, resource: MaterialResource) -> None:
        tree = resource.node_tree

        if tree is None:
            return

        resource.previous_active_node = tree.nodes.active

        tree.nodes.active = resource.image_node

    @classmethod
    def restore_active_node(cls, resource: MaterialResource) -> None:
        tree = resource.node_tree

        if tree is None:
            return

        tree.nodes.active = resource.previous_active_node

    @classmethod
    def remove_temporary_nodes(cls, resource: MaterialResource) -> None:
        if not resource.created_image_node:
            return

        tree = resource.node_tree

        if tree is None:
            return

        if resource.image_node is None:
            return

        tree.nodes.remove(resource.image_node)

        resource.image_node = None

    @classmethod
    def _create_bake_material(cls, obj: bpy.types.Object, slot: int | None):
        material = bpy.data.materials.new(
            name=f"{obj.name}_{BAKE_MATERIAL_NAME}_{str(len(obj.material_slots)).zfill(2)}"
        )
        if slot is None:
            obj.data.materials.append(material)
        elif isinstance(slot, int):
            obj.material_slots[slot].material = material
        else:
            raise AttributeError
        return material
