from __future__ import annotations

import bpy

from ..constant import BAKE_IMAGE_NODE_LABEL, BAKE_IMAGE_NODE_NAME, BAKE_MATERIAL_NAME, LOG
from ..resources.material import MaterialResource, MaterialResources
from ..runtime.context_bake import BakeContext

LOG_SCOPE = "Material Service"


class MaterialService:
    """Manage temporary material modifications during baking."""

    @classmethod
    def prepare(cls, ctx: BakeContext) -> None:
        cls.prepare_target(ctx)

        if ctx.selected_to_active:
            cls.prepare_sources(ctx)

    @classmethod
    def prepare_sources(cls, ctx: BakeContext) -> None:
        for o in ctx.sources:
            resources = MaterialResources()
            ctx.sources_materials[o.name] = resources
            cls.init_material_resources(o, resources.resources)

            for resource in resources.resources.values():
                cls.ensure_nodes(resource)
                resource.mark_prepared()

    @classmethod
    def prepare_target(cls, ctx: BakeContext) -> None:
        """
        Prepare the target object's active material for baking.
        """
        with LOG.scope(LOG_SCOPE):
            resources = MaterialResources()
            ctx.target_materials[ctx.target.name] = resources
            cls.init_material_resources(ctx.target, resources.resources)

            for resource in resources.resources.values():
                cls.ensure_nodes(resource)
                cls.ensure_image_node(resource)
                cls.assign_image(resource, ctx)
                cls.activate_image_node(resource)

                resource.mark_prepared()

    @classmethod
    def init_material_resources(cls, obj: bpy.types.Object, resources: dict[int, MaterialResource]) -> None:
        """Create all material ressources for each material slots"""

        if not obj.material_slots:
            LOG.debug(f"{obj.name} have no Material Slots")
            resources.clear()
            resources[-1] = MaterialResource(material_index=-1)
        else:
            resources.clear()
            for idx, slot in enumerate(obj.material_slots):
                LOG.debug(f"Store {slot.material.name if slot.material is not None else 'EMPTY'} for index {idx}")
                resources[idx] = MaterialResource()
                cls._store_material_info(resources[idx], obj, idx, slot.material)

    @classmethod
    def ensure_nodes(cls, resource: MaterialResource) -> None:
        """
        Ensure node-based shading is enabled.
        """
        material = resource.material

        if material is None:
            LOG.warning("Material is None")
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
            LOG.error("Tree is None")
            return

        for node in tree.nodes:
            if node.type != "TEX_IMAGE":
                continue

            if node.label == BAKE_IMAGE_NODE_LABEL:
                LOG.debug(f"Reuse Existig Image Node : {node.label}")
                resource.image_node = node
                return

        if resource.material is None:
            LOG.error("Ressource has invalid material")
            return

        LOG.debug(f"Add Image node to bake material : {resource.material.name}")
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

        if ctx.image.image is None:
            LOG.error("Image is None")
            return

        resource.image_node.image = ctx.image.image

    @classmethod
    def activate_image_node(cls, resource: MaterialResource) -> None:
        tree = resource.node_tree

        if tree is None:
            return

        resource.previous_active_node = tree.nodes.active
        LOG.debug("Set Image active")

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

        LOG.debug("Remove Temporary Image Node")
        tree.nodes.remove(resource.image_node)

        resource.image_node = None

    @classmethod
    def _create_bake_material(cls, obj: bpy.types.Object) -> bpy.types.Material:
        name = f"{obj.name}_{BAKE_MATERIAL_NAME}_{str(len(obj.material_slots)).zfill(2)}"

        if name in bpy.data.materials:
            LOG.debug(f"Reuse Existing Bake Material {name}")
            material = bpy.data.materials[name]
        else:
            LOG.debug(f"Create Bake Material {name}")
            material = bpy.data.materials.new(name=name)

        return material

    @classmethod
    def _assign_material_to_slot(cls, obj: bpy.types.Object, material: bpy.types.Material, slot: int | None) -> None:
        if slot is None:
            LOG.debug(f"Add new slot and assign material {material.name} to {obj.name}")
            obj.data.materials.append(material)
        elif isinstance(slot, int):
            LOG.debug(f"Assign material {material.name} to {obj.name}'s slot {slot}")
            obj.material_slots[slot].material = material
        else:
            raise AttributeError

    @classmethod
    def _store_material_info(
        cls, resource: MaterialResource, obj: bpy.types.Object, index: int, material: bpy.types.Material | None
    ) -> None:
        resource.object = obj
        resource.material_index = index
        if material is None:
            return
        resource.material = material
        resource.node_tree = material.node_tree
