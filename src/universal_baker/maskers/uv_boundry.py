from __future__ import annotations

from ..core.registry_masker import registry_masker
from .base import MaskerBase


class UvBoundryMasker(MaskerBase):
    """Accumulate images using their alpha channel."""

    id = "APPLY_MASK"
    name = "Apply Mask"
    description = "Mask image with the alpha channel of the mask"


classes = (UvBoundryMasker,)


def register():
    for c in classes:
        registry_masker.register(c())


def unregister():
    for c in classes:
        registry_masker.unregister(c.id)
