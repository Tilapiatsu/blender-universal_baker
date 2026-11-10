from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from ..constant import LOG, get_prefs
from ..core.registry_baker import registry_baker
from ..core.registry_definition import registry_definition
from ..parameter.baker_custom.metadata_loader import MetadataLoader as metadata_loader_custom
from ..resources.asset_external import AssetExtrenal
from ..runtime.asset_setup import BakerExecution
from ..runtime.bake_objects import BakeObjects
from ..services.asset_external_setup import AssetExternalBakeSetup
from .base import BakerBase


class ExternalBaker(BakerBase):
    """External bake defined in an external blend file."""

    id = "EXTERNAL"
    name = "EXTERNAL"
    description = "External bake defined in an external blend file."
    icon = "TEXTURE"
    blender_bake_type = "EMIT"
    accumulator_id = "ALPHA_OVER"
    asset_path: Path
    is_custom: bool = True

    @contextmanager
    def prepare_execution(
        self,
        bake_objects: BakeObjects,
    ) -> Generator[BakerExecution, Any, Any]:
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

    @classmethod
    def register_external(cls):
        prefs = get_prefs()

        for library in prefs.baker_libraries:
            library_root = Path(library.path)
            if not library_root.exists() or not library_root.is_dir():
                LOG.warning(f"Library path is not valid : {library_root}")
                continue

            assets_path = library_root / "assets"

            blend_files = [f for f in assets_path.iterdir() if f.is_file() and f.suffix.lower() == ".blend"]

            if len(blend_files) == 0:
                LOG.warning(f"No blend file found in {library.name} library")

            LOG.info(f"Registering Library : {library.name}")
            for blend_file in blend_files:
                custom_baker = cls()
                baker_name = blend_file.stem.upper().replace(" ", "_")
                custom_baker.id += f"_{baker_name}"
                custom_baker.asset_path = blend_file
                custom_baker.name = blend_file.stem.capitalize()

                LOG.info(f"Registering External Baker : {baker_name}")
                registry_baker.register(custom_baker)

                registry_definition.register_custom_lazy(
                    identifier=custom_baker.id,
                    asset_path=blend_file,
                    loader=metadata_loader_custom.load_definition,
                )


classes = (ExternalBaker,)


def register():
    for c in classes:
        baker = c()
        baker.register_external()


def unregister():
    for c in classes:
        registry_baker.unregister_custom(c.id)


def refresh():
    unregister()
    register()
