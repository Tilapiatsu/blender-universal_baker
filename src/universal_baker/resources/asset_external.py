from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..constant import PROTOTYPE_NAME


@dataclass(frozen=True)
class AssetExtrenal:
    """
    Description of an external Universal Baker's external asset.

    The actual Blender datablocks are loaded by AssetExternalService.
    """

    filepath: Path
    prototype_name: str = PROTOTYPE_NAME

    @property
    def exists(self) -> bool:
        return self.filepath.is_file()
