from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any

import bpy

from ..bakers.base import BakerBase
from ..constant import LOG
from ..core.registry_baker import registry_baker
from ..core.registry_definition import registry_definition
from ..parameter.baker_custom.metadata_loader import MetadataLoader as metadata_loader_custom
from ..resources.asset_external import AssetExtrenal
from ..runtime.asset_setup import BakerExecution
from ..runtime.bake_objects import BakeObjects
from ..services.asset_external_setup import AssetExternalBakeSetup
from ..services.material_injection import MaterialInjectionService
from ..services.modifier_injection import ModifierInjectionService
from ..services.temp_object import TempObject

if TYPE_CHECKING:
    from ..parameter.metadata import ParameterMetadata


class CustomBaker(BakerBase):
    """Custom bake defined in an external blend file."""

    id = "CUSTOM"
    name = "Custom"
    description = "Custom bake defined in an external blend file."
    icon = "TEXTURE"
    blender_bake_type = "EMIT"
    accumulator_id = "ALPHA_OVER"
    is_custom: bool = True

    @property
    def asset_path(self) -> Path | None:
        assets_path = Path(__file__).parent / "assets"
        blend_files = [
            f
            for f in assets_path.iterdir()
            if f.is_file() and f.suffix.lower() == ".blend" and f.stem == self.id.lower()
        ]

        if len(blend_files) == 0 or len(blend_files) > 1:
            LOG.error(f"{len(blend_files)} .blend files found while registering Custom Baker")
            for f in blend_files:
                LOG.debug(f.name)
            return

        return blend_files[0]

    @property
    def parameters(self) -> tuple[ParameterMetadata, ...]:
        return super().parameters

    @contextmanager
    def prepare_execution(
        self,
        bake_objects: BakeObjects,
    ) -> Generator[BakerExecution, Any, Any]:
        assert self.asset_path is not None
        asset = AssetExtrenal(filepath=self.asset_path)

        hide_render = {}

        for s in bake_objects.baker_material_objects:
            hide_render[s] = s.hide_render

        setup = AssetExternalBakeSetup.prepare(
            asset=asset,
            bake_objects=bake_objects,
        )

        try:
            yield BakerExecution(
                target=setup.target,
                cage=setup.cage,
                sources=setup.sources,
                setup=setup,
            )

        finally:
            for obj, render in hide_render.items():
                obj.hide_render = render
            setup.cleanup()

    def configure_preview(self, material: bpy.types.Material, objects: list[bpy.types.Object]) -> list[TempObject]:
        assert self.asset_path is not None
        asset = AssetExtrenal(filepath=self.asset_path)

        with AssetExternalBakeSetup.get_prototype_data(asset) as prototype_data:
            prototype = prototype_data.obj
            prototype_material = prototype_data.material

            if prototype_material is not None:
                material.use_nodes = True
                material.node_tree.nodes.clear()
                material.node_tree.nodes.new("ShaderNodeOutputMaterial")

                MaterialInjectionService.copy(source_material=prototype_material, target_material=material)

            temp_objects: list[TempObject] = []
            if len(prototype.modifiers):
                for o in objects:
                    copy = o.copy()
                    copy.name = f"{o.name}_MODIFIER_INJECTED"

                    temp_object = TempObject(new_obj=copy, recover_obj=o, cleanup=True)
                    temp_objects.append(temp_object)

                    for c in o.users_collection:
                        c.objects.link(copy)

                    ModifierInjectionService.inject(source=prototype, target=copy)

        return temp_objects

    def configure_preview_material(self, material):
        assert self.asset_path is not None
        asset = AssetExtrenal(filepath=self.asset_path)

        with AssetExternalBakeSetup.get_prototype_data(asset) as prototype_data:
            prototype_material = prototype_data.material

            if prototype_material is not None:
                material.use_nodes = True
                material.node_tree.nodes.clear()
                material.node_tree.nodes.new("ShaderNodeOutputMaterial")

                MaterialInjectionService.copy(source_material=prototype_material, target_material=material)

    def configure_preview_modifier(self, objects: list[bpy.types.Object]) -> list[TempObject]:
        assert self.asset_path is not None
        asset = AssetExtrenal(filepath=self.asset_path)

        with AssetExternalBakeSetup.get_prototype_data(asset) as prototype_data:
            prototype = prototype_data.obj

            temp_objects: list[TempObject] = []
            if len(prototype.modifiers):
                for o in objects:
                    copy = o.copy()
                    copy.name = f"{o.name}_MODIFIER_INJECTED"

                    temp_object = TempObject(new_obj=copy, recover_obj=o, cleanup=True)
                    temp_objects.append(temp_object)

                    for c in o.users_collection:
                        c.objects.link(copy)

                    ModifierInjectionService.inject(source=prototype, target=copy)

        return temp_objects

    def register_custom(self):
        if self.asset_path is None:
            return

        LOG.info(f"Registering Custom Baker : {self.id}")
        self.register_property_class()
        registry_baker.register(self)

        registry_definition.register_custom_lazy(
            identifier=self.id,
            asset_path=self.asset_path,
            loader=metadata_loader_custom.load_definition,
        )
