from __future__ import annotations

from ..constant import ICON_PACKER
from ..core.registry_accumulator import registry_accumulator
from .base import AccumulatorBase


class AlphaOverAccumulator(AccumulatorBase):
    """Accumulate images using their alpha channel."""

    id = "ALPHA_OVER"
    name = "Alpha Over"
    description = "Accumulate image using their alpha channel"
    icon = ICON_PACKER


classes = (AlphaOverAccumulator,)


def register():
    for c in classes:
        registry_accumulator.register(c())


def unregister():
    for c in classes:
        registry_accumulator.unregister(c.id)
