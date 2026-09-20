from __future__ import annotations

from pathlib import Path

from ..constant import LOG
from ..core.registry_definition import registry_definition
from ..parameter.baker_custom.metadata_loader import MetadataLoader as metadata_loader_custom


def register():
    Register.register_assets()


class Register:
    @classmethod
    def register_assets(cls):
        asset_path = Path(__file__).parent
        files = asset_path.glob("**/*.blend")

        for f in files:
            id = f.stem.upper().replace(" ", "_")
            LOG.info(f"Registering Asset : {id}")

            registry_definition.register_custom_lazy(
                identifier=id,
                asset_path=f,
                loader=metadata_loader_custom.load_definition,
            )
