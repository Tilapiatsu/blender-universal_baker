from __future__ import annotations

from ..constant import ICON_PACKER
from ..core.registry_accumulator import registry_accumulator
from .base import AccumulatorBase


class MaxAccumulator(AccumulatorBase):
    """Accumulate image keeping the brightest pixel."""

    id = "MAX"
    name = "Maximum"
    description = "Accumulate image keeping the brightest pixel"
    icon = ICON_PACKER


classes = (MaxAccumulator,)


def register():
    for c in classes:
        registry_accumulator.register(c())


def unregister():
    for c in classes:
        registry_accumulator.unregister(c.id)
