from __future__ import annotations

from enum import Enum


class OutputStage(Enum):
    BAKE = "BAKE"
    MASKED = "MASKED"
    ACCUMULATED = "ACCUMULATED"
    PACK = "PACK"
