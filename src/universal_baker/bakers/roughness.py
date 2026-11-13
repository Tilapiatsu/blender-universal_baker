from __future__ import annotations

from ..core.registry_baker import registry_baker
from ..enum.image_colorspace import ImageColorSpace
from ..enum.view_transform import DisplayDevice, ViewTransform
from ..runtime.color_management_info import ColorManagementInfo
from .base import BakerBase


class Roughness(BakerBase):
    """Bake the Normal."""

    id = "ROUGHNESS"
    name = "Roughness"
    description = "Bake Roughness"
    icon = "TEXTURE"
    blender_bake_type = "ROUGHNESS"
    accumulator_id = "ALPHA_OVER"
    clear_preview_material: bool = False
    bake_colorspace: ImageColorSpace = ImageColorSpace.NON_COLOR
    image_colorspace: ImageColorSpace = ImageColorSpace.NON_COLOR
    color_management_info = ColorManagementInfo(
        apply_view_transform=True,
        display_device=DisplayDevice.SRGB,
        view_transform=ViewTransform.RAW,
        look="None",
        exposure=0.0,
        gamma=1.0,
    )
    previewable: bool = False


classes = (Roughness,)


def register():
    for c in classes:
        baker = c()
        baker.register_local()


def unregister():
    for c in classes:
        registry_baker.unregister(c.id)
