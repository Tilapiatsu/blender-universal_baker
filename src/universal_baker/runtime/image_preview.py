from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import bpy
from bpy.utils import previews


@dataclass(slots=True)
class ImagePreviewRuntime:
    _preview_coll: dict[str, previews.ImagePreviewCollection] = field(default_factory=dict)

    def load(self, image: bpy.types.Image, baker_uuid: str) -> None:
        if image is None:
            return

        pcoll = previews.new()
        pcoll.load(image.name, str(self._get_image_path(image)), "IMAGE")

        self._preview_coll[baker_uuid] = pcoll

    def remove(self, baker_uuid: str) -> None:
        pcoll = self._preview_coll.get(baker_uuid)

        if pcoll is None:
            return

        previews.remove(pcoll)

    def update(self, image: bpy.types.Image, baker_uuid: str) -> None:
        self.remove(baker_uuid)
        self.load(image, baker_uuid)

    def get(self, baker_uuid: str) -> previews.ImagePreviewCollection | None:
        return self._preview_coll.get(baker_uuid)

    def clear(self) -> None:
        for pcoll in self._preview_coll.values():
            previews.remove(pcoll)

        self._preview_coll.clear()

    @classmethod
    def _get_image_path(cls, image: bpy.types.Image) -> Path:
        if ".<UDIM>" in image.filepath_raw:
            p = Path(image.filepath_raw)
            file_pattern = p.name.replace(".<UDIM>", "").split(".")[0]
            filepath = list(p.parent.glob(f"{file_pattern}*"))
            return filepath[0]
        else:
            return image.filepath_raw
