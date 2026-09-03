from __future__ import annotations

from pathlib import Path

import bpy

from ..resources.baker_asset import BakerAsset
from ..constant import LOG

LOG_SCOPE = "Custom Baker Service"


class BakerAssetError(RuntimeError):
    """Raised when a custom baker asset cannot be loaded."""


class BakerAssetService:
    @staticmethod
    def load_prototype(asset: BakerAsset) -> bpy.types.Object:

        with LOG.scope(LOG_SCOPE):
            LOG.debug(f"Loading Prototype : {asset.filepath}")
            filepath = Path(asset.filepath)

            if not filepath.is_file():
                raise BakerAssetError(f"Custom baker asset does not exist: {filepath}")

            with bpy.data.libraries.load(str(filepath), link=False) as (data_from, data_to):
                if asset.prototype_name not in data_from.objects:
                    raise BakerAssetError(f"Prototype object '{asset.prototype_name}' was not found in '{filepath}'.")

                data_to.objects = [asset.prototype_name]

            prototype = next(
                (obj for obj in data_to.objects if obj is not None),
                None,
            )

            if prototype is None:
                raise BakerAssetError(f"Failed to load prototype '{asset.prototype_name}'.")

            LOG.debug(f"Prototype {asset.prototype_name} properly loaded")
            return prototype
