from __future__ import annotations

from enum import Enum


class Execution(str, Enum):
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"
