# resources/baker_asset.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from ..constant import PROTOTYPE_NAME


@dataclass(frozen=True)
class BakerAsset:
    """
    Description of an external Universal Baker custom baker asset.

    The actual Blender datablocks are loaded by BakerAssetService.
    """

    filepath: Path
    prototype_name: str = PROTOTYPE_NAME

    @property
    def exists(self) -> bool:
        return self.filepath.is_file()
